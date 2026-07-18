from unittest.mock import AsyncMock, patch

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from api.models import GameModel, PlayerModel, TableTypeModel
from api.utils import get_jwt_tokens
from .routing import websocket_urlpatterns
from .utils.redis_manager import _get_redis

application = URLRouter(websocket_urlpatterns)


class PokerGameConsumerTest(TransactionTestCase):
    def setUp(self):
        self.table_type = TableTypeModel.objects.create(
            small_blind=10,
            big_blind=20,
            min_buy_in=100,
            max_buy_in=1000
        )
        self.game = GameModel.objects.create(
            open_seats='123456',
            table_type=self.table_type
        )
        self.user1 = get_user_model().objects.create_user(
            username='player1', password='testpass123')
        self.user2 = get_user_model().objects.create_user(
            username='player2', password='testpass123')

    def tearDown(self):
        async_to_sync(self._flush_redis)()

    async def _flush_redis(self):
        r = await _get_redis()
        await r.flushdb()

    def _join(self, user):
        '''Creates a player, joins the game and assigns it a seat. Returns (player, token).'''
        player = PlayerModel.objects.create(user=user)
        player.join_game(self.game, user.pk, self.table_type.min_buy_in)
        self.game.get_assigned_seat(player.pk)
        _, access_token = get_jwt_tokens(user)
        return player, access_token

    async def _sync_join(self, user):
        return await database_sync_to_async(self._join)(user)

    async def _sync_get_player(self, seat_number):
        return await database_sync_to_async(
            PlayerModel.objects.get)(game=self.game, seat_number=seat_number)

    async def _refresh_game(self):
        await database_sync_to_async(self.game.refresh_from_db)()

    def _get_to_act_seat(self):
        self.game.refresh_from_db()
        return self.game.current_turn.seat_number

    async def _sync_get_to_act_seat(self):
        return await database_sync_to_async(self._get_to_act_seat)()

    async def _connect(self, access_token):
        communicator = WebsocketCommunicator(application, f'/ws/poker/{access_token}/')
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        return communicator

    async def test_game_starts_once_two_players_join(self):
        _, token1 = await self._sync_join(self.user1)
        communicator1 = await self._connect(token1)
        await communicator1.receive_json_from(timeout=5)  # game_joined

        await self._refresh_game()
        self.assertFalse(self.game.game_started)

        _, token2 = await self._sync_join(self.user2)
        communicator2 = await self._connect(token2)

        # player1 sees player2 join
        await communicator1.receive_json_from(timeout=5)  # player_joined
        await communicator2.receive_json_from(timeout=5)  # game_joined

        await self._refresh_game()
        self.assertTrue(self.game.game_started)

        await communicator1.disconnect()
        await communicator2.disconnect()

    async def test_player_to_act_sent_to_correct_player(self):
        player1, token1 = await self._sync_join(self.user1)
        communicator1 = await self._connect(token1)
        await communicator1.receive_json_from(timeout=5)  # game_joined

        _, token2 = await self._sync_join(self.user2)
        communicator2 = await self._connect(token2)

        await communicator1.receive_json_from(timeout=5)  # player_joined
        await communicator2.receive_json_from(timeout=5)  # game_joined

        to_act_seat = await self._sync_get_to_act_seat()
        acting = player1.seat_number == to_act_seat
        acting_communicator = communicator1 if acting else communicator2
        waiting_communicator = communicator2 if acting else communicator1

        turn_event = await acting_communicator.receive_json_from(timeout=5)
        self.assertEqual(turn_event['event'], 'Your turn to act')

        self.assertTrue(await waiting_communicator.receive_nothing())

        await communicator1.disconnect()
        await communicator2.disconnect()

    async def test_player_folded_after_turn_timeout(self):
        player1, token1 = await self._sync_join(self.user1)
        communicator1 = await self._connect(token1)
        await communicator1.receive_json_from(timeout=5)  # game_joined

        with patch('websocket.consumers.asyncio.sleep', new=AsyncMock(return_value=None)):
            _, token2 = await self._sync_join(self.user2)
            communicator2 = await self._connect(token2)

            await communicator1.receive_json_from(timeout=5)  # player_joined
            await communicator2.receive_json_from(timeout=5)  # game_joined

            to_act_seat = await self._sync_get_to_act_seat()
            acting = player1.seat_number == to_act_seat
            acting_communicator = communicator1 if acting else communicator2

            turn_event = await acting_communicator.receive_json_from(timeout=5)
            self.assertEqual(turn_event['event'], 'Your turn to act')

            fold_event_1 = await communicator1.receive_json_from(timeout=5)
            fold_event_2 = await communicator2.receive_json_from(timeout=5)

        self.assertEqual(fold_event_1['event'], 'player_folded')
        self.assertEqual(fold_event_1['seat_num'], to_act_seat)
        self.assertEqual(fold_event_2['event'], 'player_folded')
        self.assertEqual(fold_event_2['seat_num'], to_act_seat)

        folded_player = await self._sync_get_player(to_act_seat)
        self.assertTrue(folded_player.is_folded)

        await communicator1.disconnect()
        await communicator2.disconnect()
