# tests/test_player_model.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import GameModel, PlayerModel, TableTypeModel


class PlayerModelTestCase(TestCase):
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

    def _join(self, user):
        player = PlayerModel.objects.create(user=user)
        player.join_game(self.game, user.pk, self.table_type.min_buy_in)
        return self.game.get_assigned_seat(player.pk)


class HoleCardsTest(PlayerModelTestCase):
    def setUp(self):
        super().setUp()
        self.users = [
            get_user_model().objects.create_user(username=f'player{i}', password='testpass123')
            for i in range(1, 7)
        ]
        for user in self.users:
            self._join(user)

        self.game.start_game()

    def test_hole_cards(self):
        for user in self.users:
            player = PlayerModel.objects.get(user=user)
            card1, card2 = player.get_hole_cards()

            self.assertEqual(len(card1), 2)
            self.assertEqual(len(card2), 2)
            self.assertNotEqual(card1, card2)
            self.assertEqual(player.cards, f"{card1},{card2}")
