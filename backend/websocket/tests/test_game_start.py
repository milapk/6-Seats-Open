from .base import PokerGameConsumerTestBase


class GameStartTest(PokerGameConsumerTestBase):
    async def test_game_starts_once_two_players_join(self):
        _, token1 = await self._sync_join(self.user1)
        communicator1 = await self._connect(token1)
        game_joined = await communicator1.receive_json_from(timeout=5)
        
        await self._refresh_game()
        self.assertFalse(self.game.game_started)

        _, token2 = await self._sync_join(self.user2)
        communicator2 = await self._connect(token2)

        # player1 sees player2 join
        await communicator1.receive_json_from(timeout=5)
        await communicator2.receive_json_from(timeout=5)

        await self._refresh_game()
        self.assertTrue(self.game.game_started)

        await communicator1.disconnect()
        await communicator2.disconnect()
