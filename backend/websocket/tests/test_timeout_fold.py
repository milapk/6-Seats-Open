from unittest.mock import AsyncMock, patch

from .base import PokerGameConsumerTestBase


class TimeoutFoldTest(PokerGameConsumerTestBase):
    async def test_player_folded_after_turn_timeout(self):
        player1, token1 = await self._sync_join(self.user1)
        communicator1 = await self._connect(token1)
        await communicator1.receive_json_from(timeout=5)

        with patch('websocket.consumers.asyncio.sleep', new=AsyncMock(return_value=None)):
            _, token2 = await self._sync_join(self.user2)
            communicator2 = await self._connect(token2)

            await communicator1.receive_json_from(timeout=5)  # player_joined
            await communicator2.receive_json_from(timeout=5)  # game_joined
            await communicator1.receive_json_from(timeout=5)  # game_started
            await communicator2.receive_json_from(timeout=5)  # game_started


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
