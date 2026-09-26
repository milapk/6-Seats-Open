import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from api.models import PlayerModel, GameModel
from .utils.game import (
    get_user,
    user_in_game,
    start_game,
    get_game_info,
    leave_game,
)
from .utils.redis_manager import (
    set_player_channel,
    get_player_channel,
    set_player_turn_deadline,
    get_player_turn_deadline,
    clear_player_turn_deadline,
    claim_turn_timeout,
)
import time


class PokerGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        self.user = await get_user(self.token)
        self.game, self.pk = await user_in_game(self.user)
        self.game_pk = self.game.pk
        if self.user and self.game:
            self.room_group_name = f'poker_{self.game.id}'
            await self.accept()

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'player_joined',
                'user_id': self.user.id
            })
            await set_player_channel(self.game.id, self.user, self.channel_name)

            self.turn_timeout_task = None
            channel_name, seat_num = await start_game(self.game)
            if channel_name:
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'game_started',
                    'user_id': self.user.id
                })
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'send_hole_cards'
                })
                deadline = await set_player_turn_deadline(self.game.id, seat_num)
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'player_to_act', 'seat_num': seat_num, 'deadline': deadline
                })
        else:
            await self.close()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if getattr(self, 'turn_timeout_task', None):
            self.turn_timeout_task.cancel()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if not isinstance(data, dict):
            return

        if data.get('event') == 'player_act':
            if not await sync_to_async(self.game.get_player_turn)(self.user):
                await self.send(text_data=json.dumps({'event': 'invalid_act', 'msg': 'Not your turn'}))
                return

            player = await sync_to_async(PlayerModel.objects.get)(user=self.user, game=self.game)
            seat_num = player.seat_number

            current_time = time.time()
            deadline_info = await get_player_turn_deadline(self.game.id, seat_num)
            if not deadline_info or deadline_info['deadline'] < current_time:
                await self.send(text_data=json.dumps({
                    'event': 'invalid_act', 'msg': 'Deadline passed'
                }))
                return

            acted = await sync_to_async(self.game.perform_player_act)(
                self.user, data.get('act'), data.get('amount')
            )
            # Make clear_player_turn_deadline(self.game.id, seat_num) before perform_player_act so
            # it prevent race conditions and then revert this if players act illegal
            if not acted:
                await self.send(text_data=json.dumps({'event': 'invalid_act', 'msg': 'Illegal move'}))
                return

            await clear_player_turn_deadline(self.game.id, seat_num)
            if getattr(self, 'turn_timeout_task', None):
                self.turn_timeout_task.cancel()
                self.turn_timeout_task = None

            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'player_acted',
                'seat_num': seat_num,
                'act': data.get('act'),
                'amount': data.get('amount')
            })

            await self._advance_turn()

    async def _enforce_turn_timeout(self, seat_num, deadline):
        await asyncio.sleep(max(0, deadline - time.time()))
        if not await claim_turn_timeout(self.game.id, seat_num):
            return
        await sync_to_async(
            PlayerModel.objects.filter(game=self.game, seat_number=seat_num).update
        )(is_folded=True)
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'player_folded',
            'seat_num': seat_num,
        })
        await self._advance_turn()

    async def _advance_turn(self):
        next_player = None
        progressed, stage = await sync_to_async(self.game.perform_next_stage)()
        if progressed:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'send_community_cards', 'stage': stage
            })
            next_player = await sync_to_async(
                lambda: GameModel.objects.values_list(
                    "current_turn", flat=True
                ).get(pk=self.game_pk)
            )()
        else:
            next_player = await sync_to_async(self.game.perform_next_player_turn)()

        if next_player:
            next_player_pk = getattr(next_player, 'pk', next_player)
            seat_num = await sync_to_async(
                lambda: PlayerModel.objects.values_list(
                    'seat_number', flat=True
                ).get(pk=next_player_pk)
            )()
            next_channel = await get_player_channel(self.game.id, seat_num)
            if next_channel:
                deadline = await set_player_turn_deadline(self.game.id, seat_num)
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'player_to_act', 'seat_num': seat_num, 'deadline': deadline
                })

    async def player_joined(self, event):
        game_info = await get_game_info(self.user)
        if event.get('user_id') == self.user.id:
            await self.send(text_data=json.dumps({'event': 'game_joined', 'data': game_info}))
        else:
            await self.send(text_data=json.dumps({'event': 'player_joined', 'data': game_info}))

    async def game_started(self, event):
        game_info = await get_game_info(self.user)
        await self.send(text_data=json.dumps({'event': 'game_started', 'data': game_info}))

    async def player_left(self, event):
        user_id = event.get('user_id')
        if user_id == self.user.id:
            leave_game(self.user)
            await self.send(text_data=json.dumps({'event': 'game_leave'}))
        else:
            await self.send(text_data=json.dumps({'event': 'player_left', 'user_id': user_id}))

    async def player_to_act(self, event):
        seat_num = event['seat_num']
        deadline = event['deadline']
        player_seat = await sync_to_async(
            lambda: PlayerModel.objects.values_list(
                "seat_number", flat=True
            ).get(pk=self.pk)
        )()
        
        self.turn_timeout_task = asyncio.create_task(
            self._enforce_turn_timeout(seat_num, deadline)
        )
        event_name = 'you_to_act' if player_seat == seat_num else 'player_to_act'
        await self.send(text_data=json.dumps({'event': event_name, 'deadline': deadline,
            'seat_num': seat_num})
        )

    async def player_acted(self, event):
        game_info = await get_game_info(self.user)
        await self.send(text_data=json.dumps(
            {'event': 'player_acted', 'seat_num': event['seat_num'], 
            'act': event['act'], 'amount': event['amount'], 'data': game_info}
        ))

    async def player_folded(self, event):
        game_info = await get_game_info(self.user)
        await self.send(text_data=json.dumps(
            {'event': 'player_folded', 'seat_num': event['seat_num'], 'data': game_info}
        ))

    async def send_hole_cards(self, event):
        cards = await sync_to_async(
            lambda: PlayerModel.objects.values_list('cards', flat=True).get(pk=self.pk)
        )()
        hole_cards = cards.split(',') if cards else []
        await self.send(text_data=json.dumps({'event': 'hole_cards', 'cards': hole_cards}))

    async def send_community_cards(self, event):
        cards = await sync_to_async(
            lambda: GameModel.objects.values_list('community_cards', flat=True).get(pk=self.game_pk)
        )()
        community_cards = cards.split(',') if cards else []
        await self.send(text_data=json.dumps({
            'event': 'community_cards', 'stage': event['stage'], 'cards': community_cards
        }))
