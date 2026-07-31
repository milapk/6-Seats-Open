# tests/test_game_model_helpers.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import GameModel, PlayerModel, PotModel, TableTypeModel


class GameModelHelpersTestCase(TestCase):
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

    def _seat_player(self, seat_number, username, is_folded=False):
        '''Directly seats a player, bypassing get_assigned_seat, so branch/edge
        tests can control the exact seat layout instead of relying on
        matchmaking geometry.'''
        user = get_user_model().objects.create_user(username=username, password='testpass123')
        player = PlayerModel.objects.create(
            user=user,
            game=self.game,
            seat_number=seat_number,
            chips_in_play=100,
            is_folded=is_folded,
        )
        self.game.open_seats = self.game.open_seats.replace(str(seat_number), '')
        self.game.num_of_players += 1
        self.game.save(update_fields=['open_seats', 'num_of_players'])
        return player


class SeatAddSubTest(GameModelHelpersTestCase):
    def test_seat_add_sub(self):
        self.assertEqual(self.game._seat_add_sub(1, 1), 2)
        self.assertEqual(self.game._seat_add_sub(1, 2), 3)
        self.assertEqual(self.game._seat_add_sub(1, 4), 5)
        self.assertEqual(self.game._seat_add_sub(1, -1), 6)
        self.assertEqual(self.game._seat_add_sub(1, -2), 5)
        self.assertEqual(self.game._seat_add_sub(1, -4), 3)
        self.assertEqual(self.game._seat_add_sub(6, 1), 1)
        self.assertEqual(self.game._seat_add_sub(1, 6), 1)
        self.assertEqual(self.game._seat_add_sub(1, 8), 3)
        self.assertEqual(self.game._seat_add_sub(1, -8), 5)
        self.assertEqual(self.game._seat_add_sub(3, 0), 3)


class GetSeatPatternsTest(GameModelHelpersTestCase):
    def test_no_seats_adjacent(self):
        count, side_by_side = self.game._get_seat_patterns([1, 3, 5])
        self.assertEqual(count, 0)
        self.assertEqual(side_by_side, [])

    def test_some_seats_adjacent(self):
        count, side_by_side = self.game._get_seat_patterns([1, 2, 4])
        self.assertEqual(count, 2)
        self.assertEqual(sorted(side_by_side), [1, 2])

    def test_all_seats_consecutive(self):
        count, side_by_side = self.game._get_seat_patterns([1, 2, 3])
        self.assertEqual(count, 3)
        self.assertEqual(sorted(side_by_side), [1, 2, 3])

    def test_adjacency_wraps_around_table(self):
        count, side_by_side = self.game._get_seat_patterns([6, 1])
        self.assertEqual(count, 2)
        self.assertEqual(sorted(side_by_side), [1, 6])


class CheckSidesTest(GameModelHelpersTestCase):
    def test_no_neighbors_taken(self):
        self.assertEqual(self.game._check_sides(1, [3, 4]), 0)

    def test_one_neighbor_taken(self):
        self.assertEqual(self.game._check_sides(1, [2]), 1)

    def test_both_neighbors_taken(self):
        self.assertEqual(self.game._check_sides(1, [2, 6]), 2)

    def test_neighbor_check_wraps_around_table(self):
        self.assertEqual(self.game._check_sides(6, [1]), 1)


class GetNextTakenSeatTest(GameModelHelpersTestCase):
    def test_no_players_returns_none(self):
        self.assertIsNone(self.game._get_next_taken_seat(1))

    def test_finds_next_taken_seat(self):
        self._seat_player(2, 'p1')
        self._seat_player(5, 'p2')
        self.assertEqual(self.game._get_next_taken_seat(1), 2)
        self.assertEqual(self.game._get_next_taken_seat(2), 5)

    def test_wraps_around_table(self):
        self._seat_player(2, 'p1')
        self.assertEqual(self.game._get_next_taken_seat(3), 2)

    def test_full_circle_returns_to_start_seat(self):
        self._seat_player(3, 'p1')
        self.assertEqual(self.game._get_next_taken_seat(3), 3)


class CreateDeckTest(GameModelHelpersTestCase):
    def test_deck_has_52_unique_two_char_cards(self):
        deck = self.game._create_deck()
        cards = deck.split(',')
        self.assertEqual(len(cards), 52)
        self.assertEqual(len(set(cards)), 52)
        self.assertTrue(all(len(card) == 2 for card in cards))

    def test_deck_is_shuffled(self):
        ordered = ','.join(
            f'{value}{suit}'
            for value in ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
            for suit in ['c', 's', 'h', 'd']
        )
        self.assertNotEqual(self.game._create_deck(), ordered)


class DealCardsTest(GameModelHelpersTestCase):
    def test_deals_two_cards_per_player_and_skips_folded(self):
        p1 = self._seat_player(1, 'p1')
        p2 = self._seat_player(2, 'p2')
        folded = self._seat_player(3, 'folded', is_folded=True)

        self.game.cards = '2c,3c,4c,5c'
        self.game.save(update_fields=['cards'])

        self.game._deal_cards(self.game)

        p1.refresh_from_db()
        p2.refresh_from_db()
        folded.refresh_from_db()

        self.assertEqual(p1.cards, '2c,3c')
        self.assertEqual(p2.cards, '4c,5c')
        self.assertIsNone(folded.cards)
        self.assertEqual(self.game.cards, '')


class GetCentricAdjustedSeatsTest(GameModelHelpersTestCase):
    def test_returns_none_if_player_has_no_seat(self):
        user = get_user_model().objects.create_user(username='noseat', password='testpass123')
        player = PlayerModel.objects.create(user=user, game=self.game, chips_in_play=100)
        self.assertIsNone(self.game._get_centric_adjusted_seats(player.pk))

    def test_rotates_so_requesting_player_is_first(self):
        self._seat_player(1, 'p1')
        p3 = self._seat_player(3, 'p3')

        seats = self.game._get_centric_adjusted_seats(p3.pk)

        # p3 sits at seat 3; rotated order should be [3, 4, 5, 6, 1, 2].
        self.assertEqual(seats[1]['username'], 'p3')
        self.assertEqual(seats[1]['actual_seat'], 3)
        self.assertIsNone(seats[2])  # seat 4, empty
        self.assertIsNone(seats[3])  # seat 5, empty
        self.assertIsNone(seats[4])  # seat 6, empty
        self.assertEqual(seats[5]['username'], 'p1')
        self.assertEqual(seats[5]['actual_seat'], 1)
        self.assertIsNone(seats[6])  # seat 2, empty

    def test_includes_chips_and_id(self):
        p1 = self._seat_player(1, 'p1')

        seats = self.game._get_centric_adjusted_seats(p1.pk)

        self.assertEqual(seats[1]['chips'], p1.chips_in_play)
        self.assertEqual(seats[1]['id'], p1.id)


class GetAssignedSeatTest(GameModelHelpersTestCase):
    def _new_joiner(self, username):
        user = get_user_model().objects.create_user(username=username, password='testpass123')
        player = PlayerModel.objects.create(user=user, game=self.game, chips_in_play=100)
        self.game.num_of_players += 1
        self.game.save(update_fields=['num_of_players'])
        return player

    def test_first_player_gets_seat_one(self):
        player = self._new_joiner('p1')

        seat = self.game.get_assigned_seat(player.pk)

        self.assertEqual(seat, 1)
        player.refresh_from_db()
        self.assertEqual(player.seat_number, 1)
        self.game.refresh_from_db()
        self.assertNotIn('1', self.game.open_seats)

    def test_second_player_seated_opposite_first(self):
        self._seat_player(1, 'p1')
        player = self._new_joiner('p2')

        seat = self.game.get_assigned_seat(player.pk)

        self.assertEqual(seat, 4)

    def test_fourth_player_all_side_by_side_sits_opposite_middle(self):
        self._seat_player(1, 'p1')
        self._seat_player(2, 'p2')
        self._seat_player(3, 'p3')
        player = self._new_joiner('p4')

        seat = self.game.get_assigned_seat(player.pk)

        self.assertEqual(seat, 5)

    def test_fourth_player_two_side_by_side_plus_lone_sits_beside_lone(self):
        self._seat_player(1, 'p1')
        self._seat_player(2, 'p2')
        self._seat_player(4, 'p3')
        player = self._new_joiner('p4')

        seat = self.game.get_assigned_seat(player.pk)

        self.assertEqual(seat, 5)

    def test_fifth_player_gets_a_valid_open_seat(self):
        self._seat_player(1, 'p1')
        self._seat_player(2, 'p2')
        self._seat_player(3, 'p3')
        self._seat_player(5, 'p4')
        open_before = [int(s) for s in self.game.open_seats]
        player = self._new_joiner('p5')

        seat = self.game.get_assigned_seat(player.pk)

        self.assertIn(seat, open_before)

    def test_third_player_two_side_by_side_sits_opposite_one_of_them(self):
        self._seat_player(1, 'p1')
        self._seat_player(2, 'p2')
        player = self._new_joiner('p3')

        seat = self.game.get_assigned_seat(player.pk)

        self.assertIn(seat, (4, 5))


class GetGameInfoTest(GameModelHelpersTestCase):
    def test_returns_info_for_seated_player(self):
        p1 = self._seat_player(1, 'p1')
        self._seat_player(3, 'p2')

        info = self.game.get_game_info(p1.pk)

        self.assertEqual(info['small_blind'], self.table_type.small_blind)
        self.assertEqual(info['big_blind'], self.table_type.big_blind)
        self.assertEqual(info['num_of_players'], self.game.num_of_players)
        self.assertEqual(info['seats'], self.game._get_centric_adjusted_seats(p1.pk))

    def test_returns_empty_dict_for_player_without_seat(self):
        user = get_user_model().objects.create_user(username='noseat', password='testpass123')
        player = PlayerModel.objects.create(user=user, game=self.game, chips_in_play=100)

        info = self.game.get_game_info(player.pk)

        self.assertEqual(info, {})


class StartGameTest(GameModelHelpersTestCase):
    def test_returns_none_with_fewer_than_two_players(self):
        self._seat_player(1, 'p1')

        result = self.game.start_game()

        self.assertIsNone(result)
        self.game.refresh_from_db()
        self.assertFalse(self.game.game_started)

    def test_returns_none_if_already_started(self):
        self._seat_player(1, 'p1')
        self._seat_player(2, 'p2')
        self.game.start_game()

        result = self.game.start_game()

        self.assertIsNone(result)

    def test_heads_up_posts_blinds_and_deals_cards(self):
        p1 = self._seat_player(1, 'p1')
        p2 = self._seat_player(2, 'p2')

        # dealer_position starts at 0 -> dealer=seat1, sb=seat2, bb=seat1
        # (wraps, only two seats taken), to_act=seat2.
        to_act_seat = self.game.start_game()

        self.assertEqual(to_act_seat, 2)
        self.game.refresh_from_db()
        p1.refresh_from_db()
        p2.refresh_from_db()

        self.assertTrue(self.game.game_started)
        self.assertEqual(self.game.betting_stage, 0)
        self.assertEqual(self.game.current_turn_id, p2.id)

        # seat1 (p1) ends up posting the big blind, seat2 (p2) the small blind.
        self.assertEqual(p1.street_bet, self.table_type.big_blind)
        self.assertEqual(p1.total_bet, self.table_type.big_blind)
        self.assertEqual(p1.chips_in_play, 100 - self.table_type.big_blind)
        self.assertEqual(p2.street_bet, self.table_type.small_blind)
        self.assertEqual(p2.total_bet, self.table_type.small_blind)
        self.assertEqual(p2.chips_in_play, 100 - self.table_type.small_blind)

        pot = PotModel.objects.get(game=self.game)
        self.assertEqual(pot.pot_money, self.table_type.small_blind + self.table_type.big_blind)
        self.assertCountEqual(pot.players.all(), [p1, p2])

        for player in (p1, p2):
            self.assertIsNotNone(player.cards)
            card1, card2 = player.cards.split(',')
            self.assertEqual(len(card1), 2)
            self.assertEqual(len(card2), 2)

    def test_three_handed_dealer_acts_first(self):
        p1 = self._seat_player(1, 'p1')
        self._seat_player(2, 'p2')
        self._seat_player(3, 'p3')

        to_act_seat = self.game.start_game()

        self.assertEqual(to_act_seat, 1)
        self.game.refresh_from_db()
        self.assertEqual(self.game.current_turn_id, p1.id)
        self.assertEqual(self.game.dealer_position, 1)

    def test_blind_is_capped_when_player_short_stacked(self):
        p1 = self._seat_player(1, 'p1')
        self._seat_player(2, 'p2')
        p1.chips_in_play = 5  # less than big blind
        p1.save(update_fields=['chips_in_play'])

        self.game.start_game()

        p1.refresh_from_db()
        self.assertEqual(p1.street_bet, 5)
        self.assertEqual(p1.chips_in_play, 0)


class GetPlayerTurnTest(GameModelHelpersTestCase):
    def test_true_for_player_to_act(self):
        self._seat_player(1, 'p1')
        p2 = self._seat_player(2, 'p2')
        self.game.start_game()
        self.game.refresh_from_db()

        self.assertTrue(self.game.get_player_turn(p2.user))

    def test_false_for_player_not_to_act(self):
        p1 = self._seat_player(1, 'p1')
        self._seat_player(2, 'p2')
        self.game.start_game()
        self.game.refresh_from_db()

        self.assertFalse(self.game.get_player_turn(p1.user))


class PerformPlayerActTestCase(GameModelHelpersTestCase):
    def setUp(self):
        super().setUp()
        self.p1 = self._seat_player(1, 'p1')
        self.p2 = self._seat_player(2, 'p2')
        self.p3 = self._seat_player(3, 'p3')
        self.pot = PotModel.objects.create(game=self.game, pot_money=0)
        self.game.betting_stage = 0
        self.game.current_turn = self.p1
        self.game.save(update_fields=['betting_stage', 'current_turn'])

    def _refresh(self):
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.p3.refresh_from_db()
        self.game.refresh_from_db()
        self.pot.refresh_from_db()


class PerformPlayerActTurnGuardTest(PerformPlayerActTestCase):
    def test_returns_false_when_not_players_turn(self):
        result = self.game.perform_player_act(self.p2.user, 'fold')

        self.assertFalse(result)
        self._refresh()
        self.assertFalse(self.p2.is_folded)
        self.assertEqual(self.game.current_turn_id, self.p1.id)

    def test_returns_false_for_unknown_action(self):
        result = self.game.perform_player_act(self.p1.user, 'raise')

        self.assertFalse(result)
        self._refresh()
        self.assertEqual(self.game.current_turn_id, self.p1.id)


class PerformPlayerActFoldTest(PerformPlayerActTestCase):
    def test_fold_marks_player_and_advances_turn(self):
        result = self.game.perform_player_act(self.p1.user, 'fold')

        self.assertTrue(result)
        self._refresh()
        self.assertTrue(self.p1.is_folded)
        self.assertTrue(self.p1.had_acted)
        self.assertEqual(self.game.current_turn_id, self.p2.id)


class PerformPlayerActBetTest(PerformPlayerActTestCase):
    def test_valid_bet_updates_player_and_pot(self):
        result = self.game.perform_player_act(self.p1.user, 'bet', amount=50)

        self.assertTrue(result)
        self._refresh()
        self.assertEqual(self.p1.street_bet, 50)
        self.assertEqual(self.p1.total_bet, 50)
        self.assertEqual(self.p1.chips_in_play, 50)
        self.assertTrue(self.p1.had_acted)
        self.assertFalse(self.p1.all_in)
        self.assertEqual(self.pot.pot_money, 50)
        self.assertIn(self.p1, self.pot.players.all())
        self.assertEqual(self.game.current_turn_id, self.p2.id)

    def test_bet_exceeding_chips_in_play_is_rejected(self):
        result = self.game.perform_player_act(self.p1.user, 'bet', amount=150)

        self.assertFalse(result)
        self._refresh()
        self.assertEqual(self.p1.chips_in_play, 100)
        self.assertEqual(self.game.current_turn_id, self.p1.id)

    def test_zero_or_negative_bet_is_rejected(self):
        self.assertFalse(self.game.perform_player_act(self.p1.user, 'bet', amount=0))
        self.assertFalse(self.game.perform_player_act(self.p1.user, 'bet', amount=-10))

    def test_bet_of_entire_stack_sets_all_in(self):
        result = self.game.perform_player_act(self.p1.user, 'bet', amount=100)

        self.assertTrue(result)
        self._refresh()
        self.assertTrue(self.p1.all_in)
        self.assertEqual(self.p1.chips_in_play, 0)


class PerformPlayerActCallTest(PerformPlayerActTestCase):
    def test_call_matching_highest_bet_succeeds(self):
        self.game.perform_player_act(self.p1.user, 'bet', amount=50)

        result = self.game.perform_player_act(self.p2.user, 'call', amount=50)

        self.assertTrue(result)
        self._refresh()
        self.assertEqual(self.p2.street_bet, 50)
        self.assertEqual(self.p2.total_bet, 50)
        self.assertEqual(self.p2.chips_in_play, 50)
        self.assertFalse(self.p2.all_in)
        self.assertEqual(self.pot.pot_money, 100)

    def test_call_with_wrong_amount_is_rejected(self):
        self.game.perform_player_act(self.p1.user, 'bet', amount=50)

        result = self.game.perform_player_act(self.p2.user, 'call', amount=40)

        self.assertFalse(result)
        self._refresh()
        self.assertEqual(self.p2.street_bet, 0)

    def test_call_exceeding_chips_in_play_is_rejected(self):
        self.game.perform_player_act(self.p1.user, 'bet', amount=50)

        result = self.game.perform_player_act(self.p2.user, 'call', amount=150)

        self.assertFalse(result)

    def test_short_all_in_call_is_allowed(self):
        self.game.perform_player_act(self.p1.user, 'bet', amount=100)  # p1 all-in
        self.p2.chips_in_play = 30
        self.p2.save(update_fields=['chips_in_play'])

        result = self.game.perform_player_act(self.p2.user, 'call', amount=30)

        self.assertTrue(result)
        self._refresh()
        self.assertTrue(self.p2.all_in)
        self.assertEqual(self.p2.chips_in_play, 0)
        self.assertEqual(self.p2.street_bet, 30)


class PerformPlayerActCheckTest(PerformPlayerActTestCase):
    def test_check_allowed_when_no_bet_facing(self):
        result = self.game.perform_player_act(self.p1.user, 'check')

        self.assertTrue(result)
        self._refresh()
        self.assertTrue(self.p1.had_acted)
        self.assertEqual(self.p1.current_bet, 0)
        self.assertEqual(self.game.current_turn_id, self.p2.id)

    def test_check_rejected_when_facing_a_bet(self):
        self.game.perform_player_act(self.p1.user, 'bet', amount=50)

        result = self.game.perform_player_act(self.p2.user, 'check')

        self.assertFalse(result)

    def test_check_rejected_if_player_already_acted(self):
        self.p1.had_acted = True
        self.p1.save(update_fields=['had_acted'])

        result = self.game.perform_player_act(self.p1.user, 'check')

        self.assertFalse(result)


class PerformPlayerActTurnAdvanceTest(PerformPlayerActTestCase):
    def test_turn_skips_folded_and_all_in_players(self):
        self.p2.is_folded = True
        self.p3.all_in = True
        self.p2.save(update_fields=['is_folded'])
        self.p3.save(update_fields=['all_in'])

        result = self.game.perform_player_act(self.p1.user, 'check')

        self.assertTrue(result)
        self._refresh()
        # Only p1 remains eligible to act, loop wraps back to them.
        self.assertEqual(self.game.current_turn_id, self.p1.id)

    def test_current_turn_left_stale_when_no_one_left_to_act(self):
        self.game.perform_player_act(self.p1.user, 'fold')
        self.game.perform_player_act(self.p2.user, 'fold')

        self.game.perform_player_act(self.p3.user, 'fold')

        self.game.refresh_from_db()
        self.assertEqual(self.game.current_turn_id, self.p3.id)


class PerformNextStageTestCase(GameModelHelpersTestCase):
    def setUp(self):
        super().setUp()
        self.p1 = self._seat_player(1, 'p1')
        self.p2 = self._seat_player(2, 'p2')
        self.p3 = self._seat_player(3, 'p3')
        self.game.betting_stage = 0
        self.game.dealer_position = 1
        self.game.cards = '2c,3c,4c,5c,6c,7c'
        self.game.community_cards = None
        self.game.game_started = True
        self.game.save(update_fields=[
            'betting_stage', 'dealer_position', 'cards', 'community_cards', 'game_started'])

    def _set_players(self, player_fields):
        for player, values in player_fields.items():
            for attr, value in values.items():
                setattr(player, attr, value)
            player.save(update_fields=list(values.keys()))


class PerformNextStageGuardsTest(PerformNextStageTestCase):
    def test_blocked_when_a_player_still_needs_to_act(self):
        self._set_players({
            self.p1: {'had_acted': True, 'street_bet': 20},
            self.p2: {'had_acted': True, 'street_bet': 20},
            self.p3: {'had_acted': False, 'street_bet': 20},
        })

        advanced, stage = self.game.perform_next_stage()

        self.assertFalse(advanced)
        self.assertIsNone(stage)
        self.game.refresh_from_db()
        self.assertEqual(self.game.betting_stage, 0)

    def test_blocked_when_bets_not_equalized(self):
        self._set_players({
            self.p1: {'had_acted': True, 'street_bet': 20},
            self.p2: {'had_acted': True, 'street_bet': 20},
            self.p3: {'had_acted': True, 'street_bet': 10},
        })

        advanced, stage = self.game.perform_next_stage()

        self.assertFalse(advanced)
        self.assertIsNone(stage)

    def test_all_in_player_does_not_block_advance(self):
        # p1 is short-stacked and all-in for less than the table-high bet;
        # p2/p3 (not all-in) have matched each other at the real high bet.
        self._set_players({
            self.p1: {'had_acted': False, 'all_in': True, 'street_bet': 20},
            self.p2: {'had_acted': True, 'street_bet': 50},
            self.p3: {'had_acted': True, 'street_bet': 50},
        })

        advanced, stage = self.game.perform_next_stage()

        self.assertTrue(advanced)
        self.assertEqual(stage, 'Flop')

    def test_no_advance_past_showdown(self):
        self.game.betting_stage = 4
        self.game.save(update_fields=['betting_stage'])

        advanced, stage = self.game.perform_next_stage()

        self.assertFalse(advanced)
        self.assertIsNone(stage)


class PerformNextStageDealingTest(PerformNextStageTestCase):
    def _mark_all_acted_and_equal(self, street_bet=20):
        self._set_players({
            self.p1: {'had_acted': True, 'street_bet': street_bet},
            self.p2: {'had_acted': True, 'street_bet': street_bet},
            self.p3: {'had_acted': True, 'street_bet': street_bet},
        })

    def test_advances_to_flop_deals_three_cards_and_resets_bets(self):
        self._mark_all_acted_and_equal()

        advanced, stage = self.game.perform_next_stage()

        self.assertTrue(advanced)
        self.assertEqual(stage, 'Flop')
        self.game.refresh_from_db()
        self.assertEqual(self.game.betting_stage, 1)
        self.assertEqual(self.game.community_cards, '2c,3c,4c')
        self.assertEqual(self.game.cards, '5c,6c,7c')

        for player in (self.p1, self.p2, self.p3):
            player.refresh_from_db()
            self.assertEqual(player.street_bet, 0)
            self.assertEqual(player.current_bet, 0)
            self.assertFalse(player.had_acted)

        self.assertEqual(self.game.current_turn_id, self.p2.id)

    def test_advances_to_turn_deals_one_card(self):
        self.game.betting_stage = 1
        self.game.community_cards = '2c,3c,4c'
        self.game.cards = '5c,6c,7c'
        self.game.save(update_fields=['betting_stage', 'community_cards', 'cards'])
        self._mark_all_acted_and_equal(street_bet=0)

        advanced, stage = self.game.perform_next_stage()

        self.assertTrue(advanced)
        self.assertEqual(stage, 'Turn')
        self.game.refresh_from_db()
        self.assertEqual(self.game.community_cards, '2c,3c,4c,5c')
        self.assertEqual(self.game.cards, '6c,7c')

    def test_reaching_showdown_clears_turn_and_splits_pots(self):
        self.game.betting_stage = 3
        self.game.save(update_fields=['betting_stage'])
        self._set_players({
            self.p1: {'had_acted': True, 'all_in': True, 'total_bet': 50, 'street_bet': 50},
            self.p2: {'had_acted': True, 'total_bet': 100, 'street_bet': 100},
            self.p3: {'had_acted': True, 'total_bet': 100, 'street_bet': 100},
        })

        advanced, stage = self.game.perform_next_stage()

        self.assertTrue(advanced)
        self.assertEqual(stage, 'Showdown')
        self.game.refresh_from_db()
        self.assertEqual(self.game.betting_stage, 4)
        self.assertIsNone(self.game.current_turn)

        pots = list(PotModel.objects.filter(game=self.game).order_by('order'))
        self.assertEqual(len(pots), 2)
        self.assertEqual(pots[0].cap, 50)
        self.assertEqual(pots[0].pot_money, 150)
        self.assertEqual(pots[1].cap, 100)
        self.assertEqual(pots[1].pot_money, 100)


class CalculateSidePotsTest(GameModelHelpersTestCase):
    def setUp(self):
        super().setUp()
        self.p1 = self._seat_player(1, 'p1')
        self.p2 = self._seat_player(2, 'p2')
        self.p3 = self._seat_player(3, 'p3')

    def test_single_pot_when_no_one_is_all_in(self):
        for player in (self.p1, self.p2, self.p3):
            player.total_bet = 20
            player.save(update_fields=['total_bet'])

        pots = list(self.game.calculate_side_pots())

        self.assertEqual(len(pots), 1)
        self.assertEqual(pots[0].cap, 20)
        self.assertEqual(pots[0].pot_money, 60)
        self.assertCountEqual(pots[0].players.all(), [self.p1, self.p2, self.p3])

    def test_all_in_creates_main_and_side_pot_excluding_folded_from_eligibility(self):
        self.p1.total_bet = 50  # short-stacked all-in
        self.p2.total_bet = 100
        self.p3.total_bet = 100
        self.p3.is_folded = True
        self.p1.save(update_fields=['total_bet'])
        self.p2.save(update_fields=['total_bet'])
        self.p3.save(update_fields=['total_bet', 'is_folded'])

        pots = list(self.game.calculate_side_pots())

        self.assertEqual(len(pots), 2)
        main_pot, side_pot = pots
        self.assertEqual(main_pot.cap, 50)
        self.assertEqual(main_pot.pot_money, 150)
        self.assertCountEqual(main_pot.players.all(), [self.p1, self.p2])

        self.assertEqual(side_pot.cap, 100)
        self.assertEqual(side_pot.pot_money, 100)
        self.assertCountEqual(side_pot.players.all(), [self.p2])

    def test_no_contributions_leaves_no_pots(self):
        PotModel.objects.create(game=self.game, pot_money=0)

        pots = list(self.game.calculate_side_pots())

        self.assertEqual(pots, [])
        self.assertEqual(PotModel.objects.filter(game=self.game).count(), 0)
