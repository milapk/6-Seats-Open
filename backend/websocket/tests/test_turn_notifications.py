from .base import PokerGameConsumerTestBase


class TurnNotificationTest(PokerGameConsumerTestBase):
    async def test_player_to_act_sent_to_correct_player(self):
        player1, token1 = await self._sync_join(self.user1)
        communicator1 = await self._connect(token1)
        await communicator1.receive_json_from(timeout=5)

        _, token2 = await self._sync_join(self.user2)
        communicator2 = await self._connect(token2)

        await communicator1.receive_json_from(timeout=5) # player_joined
        await communicator2.receive_json_from(timeout=5) # game_joined
        await communicator1.receive_json_from(timeout=5) # game_started
        await communicator2.receive_json_from(timeout=5) # game_started

        to_act_seat = await self._sync_get_to_act_seat()
        acting = player1.seat_number == to_act_seat
        acting_communicator = communicator1 if acting else communicator2
        waiting_communicator = communicator2 if acting else communicator1

        turn_event = await acting_communicator.receive_json_from(timeout=5)
        self.assertEqual(turn_event['event'], 'Your turn to act')

        self.assertTrue(await waiting_communicator.receive_nothing())

        await communicator1.disconnect()
        await communicator2.disconnect()
