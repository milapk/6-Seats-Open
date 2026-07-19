# tests/test_get_hole_cards.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import GameModel, PlayerModel, TableTypeModel


class HoleCardsTest(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username='playeer1',
            password='testpass123'
        )
        self.user2 = get_user_model().objects.create_user(
            username='playerr2',
            password='testpass123'
        )
        self.user3 = get_user_model().objects.create_user(
            username='playrer3',
            password='testpass123'
        )
        self.user4 = get_user_model().objects.create_user(
            username='playerr4',
            password='testpass123'
        )
        self.user5 = get_user_model().objects.create_user(
            username='playrer5',
            password='testpass123'
        )
        self.user6 = get_user_model().objects.create_user(
            username='plaryer6',
            password='testpass123'
        )
        self.users = [self.user1, self.user2, self.user3, self.user4, self.user5, self.user6]

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

        for user in self.users:
            self._join(user)

        self.game.start_game()

    def _join(self, user):
        player = PlayerModel.objects.create(user=user)
        player.join_game(self.game, user.pk, self.table_type.min_buy_in)
        return self.game.get_assigned_seat(player.pk)

    def test_hole_cards(self):
        for user in self.users:
            player = PlayerModel.objects.get(user=user)
            card1, card2 = player.get_hole_cards()

            self.assertEqual(len(card1), 2)
            self.assertEqual(len(card2), 2)
            self.assertNotEqual(card1, card2)
            self.assertEqual(player.cards, f"{card1},{card2}")
