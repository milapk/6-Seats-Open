import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from api.models import PlayerModel
from .utils.game import (
    get_user,
    user_in_game,
    start_game,
    get_game_info,
    leave_game,
)
from .utils.redis_manager import (
    set_player_channel,
    set_player_turn_deadline,
    get_player_turn_deadline,
    clear_player_turn_deadline,
)


class PokerGameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        self.user = await get_user(self.token)
        self.game = await user_in_game(self.user)
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
                await self.channel_layer.send(channel_name, {'type': 'player_to_act', 'seat_num': seat_num})
        else:
            await self.close()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if getattr(self, 'turn_timeout_task', None):
            self.turn_timeout_task.cancel()

    async def receive(self, text_data):
        json.loads(text_data)

    async def _enforce_turn_timeout(self, seat_num):
        await asyncio.sleep(120)
        info = await get_player_turn_deadline(self.game.id, seat_num)
        if info and not info['player_acted']:
            await sync_to_async(PlayerModel.objects.filter(game=self.game, seat_number=seat_num).update)(is_folded=True)
            await clear_player_turn_deadline(self.game.id, seat_num)
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'player_folded',
                'seat_num': seat_num,
            })

    async def player_joined(self, event):
        game_info = await get_game_info(self.user)
        if event.get('user_id') == self.user.id:
            await self.send(text_data=json.dumps({'event': 'game_joined', 'data': game_info}))
        else:
            await self.send(text_data=json.dumps({'event': 'player_joined', 'data': game_info}))

    async def player_left(self, event):
        user_id = event.get('user_id')
        if user_id == self.user.id:
            leave_game(self.user)
            await self.send(text_data=json.dumps({'event': 'game_leave'}))
        else:
            await self.send(text_data=json.dumps({'event': 'player_left', 'user_id': user_id}))

    async def player_to_act(self, event):
        seat_num = event['seat_num']
        await set_player_turn_deadline(self.game.id, seat_num)
        self.turn_timeout_task = asyncio.create_task(self._enforce_turn_timeout(seat_num))
        await self.send(text_data=json.dumps({'event': 'Your turn to act'}))

    async def player_folded(self, event):
        game_info = await get_game_info(self.user)
        await self.send(text_data=json.dumps({'event': 'player_folded', 'seat_num': event['seat_num'], 'data': game_info}))

    async def send_cards(self, event):
        await self.send(text_data=json.dumps({}))
