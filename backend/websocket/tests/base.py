from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from api.models import GameModel, PlayerModel, TableTypeModel
from api.utils import get_jwt_tokens
from ..routing import websocket_urlpatterns
from ..utils.redis_manager import _get_redis

application = URLRouter(websocket_urlpatterns)


class PokerGameConsumerTestBase(TransactionTestCase):
    def setUp(self):
        self.table_type = TableTypeModel.objects.create(
            small_blind=1,
            big_blind=2,
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
