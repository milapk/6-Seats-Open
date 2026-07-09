# tests/test_seat_assignment.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import GameModel, PlayerModel, TableTypeModel

class SeatAssignmentTest(TestCase):
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

    def test_seat_assignment(self):
        seat1 = self._join(self.user1)
        seat2 = self._join(self.user2)
        seat3 = self._join(self.user3)
        seat4 = self._join(self.user4)
        seat5 = self._join(self.user5)
        seat6 = self._join(self.user6)

        # Verify open seats updated
        print(str(seat1), self.user1.username)
        print(str(seat2), self.user2.username)
        print(str(seat3), self.user3.username)
        print(str(seat4), self.user4.username)
        print(str(seat5), self.user5.username)
        print(str(seat6), self.user6.username)

        self.assertNotIn(str(seat1), self.game.open_seats)
        self.assertNotIn(str(seat2), self.game.open_seats)
        self.assertNotIn(str(seat3), self.game.open_seats)
        self.assertNotIn(str(seat4), self.game.open_seats)
        self.assertNotIn(str(seat5), self.game.open_seats)
        self.assertNotIn(str(seat6), self.game.open_seats)
