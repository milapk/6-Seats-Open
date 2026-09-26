from .base import PokerGameConsumerTestBase

class PlayerActions(PokerGameConsumerTestBase):
    async def _start_and_get_acting(self):
        '''Starts a heads-up game and consumes the turn notifications.
        Returns (acting_communicator, waiting_communicator).'''
        player1, communicator1, communicator2 = await self._start_heads_up()

        to_act_seat = await self._sync_get_to_act_seat()
        acting = player1.seat_number == to_act_seat
        acting_communicator = communicator1 if acting else communicator2
        waiting_communicator = communicator2 if acting else communicator1

        await self._receive(acting_communicator, 'you_to_act')
        await self._receive(waiting_communicator, 'player_to_act')
        return acting_communicator, waiting_communicator

    async def _act_and_assert(self, actor, observer, act, amount):
        '''Sends an act from actor and asserts both sides receive the matching player_acted.'''
        seat = await self._sync_get_to_act_seat()
        await actor.send_json_to({'event': 'player_act', 'act': act, 'amount': amount})
        for communicator in (actor, observer):
            res = await self._receive(communicator, 'player_acted')
            self.assertEqual(res['seat_num'], seat)
            self.assertEqual(res['act'], act)
            self.assertEqual(res['amount'], amount)

    async def test_player_bet(self):
        acting, waiting = await self._start_and_get_acting()
        print("\n----------------------")

        await self._act_and_assert(acting, waiting, 'call', 1)
        await self._receive_all([acting, waiting])  # turn notifications
        
        await self._act_and_assert(waiting, acting, 'check', 0)
        print("\n----------------------")
        await self._receive_all([acting, waiting])  # next event for each
        await self._receive_all([acting, waiting])

        await self._act_and_assert(acting, waiting, 'bet', 98)
        await self._receive_all([acting, waiting])  # turn notifications

        await self._act_and_assert(waiting, acting, 'call', 98)
        print("\n----------------------")
        await self._receive_all([acting, waiting])  # turn notifications
        await self._receive_all([acting, waiting])  # turn notifications



        await self._disconnect(acting, waiting)
