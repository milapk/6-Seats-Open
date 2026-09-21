from .base import PokerGameConsumerTestBase

class PlayerActions(PokerGameConsumerTestBase):
    async def test_player_check(self):
        player1, token1 = await self._sync_join(self.user1)
        communicator1 = await self._connect(token1)
        await communicator1.receive_json_from(timeout=5) # game_joined

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

        await acting_communicator.send_json_to({'event': 'player_act', 'act': 'bet', 'amount': 2})
        res = await acting_communicator.receive_json_from()
        self.assertEqual(res['event'], 'player_acted')
        self.assertEqual(res['seat'], to_act_seat)
        self.assertEqual(res['act'], 'bet')
        self.assertEqual(res['amount'], 2)

        res = await waiting_communicator.receive_json_from()
        self.assertEqual(res['event'], 'player_acted')
        self.assertEqual(res['seat'], to_act_seat)
        self.assertEqual(res['act'], 'bet')
        self.assertEqual(res['amount'], 2)

        await communicator1.disconnect()
        await communicator2.disconnect()