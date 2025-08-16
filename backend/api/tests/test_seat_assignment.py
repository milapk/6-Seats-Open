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
        self.game = GameModel.objects.create(
            open_seats='123456',
            table_type=TableTypeModel.objects.create(
                small_blind=10,
                big_blind=20,
                min_buy_in=100,
                max_buy_in=1000
            )
        )

    def test_seat_assignment(self):
        # Player 1 joins
        player1 = PlayerModel.objects.create(
            user=self.user1,
            game=self.game
        )
        player2 = PlayerModel.objects.create(
            user=self.user2,
            game=self.game
        )
        player3 = PlayerModel.objects.create(
            user=self.user3,
            game=self.game
        )
        player4 = PlayerModel.objects.create(
            user=self.user4,
            game=self.game
        )
        player5 = PlayerModel.objects.create(
            user=self.user5,
            game=self.game
        )
        player6 = PlayerModel.objects.create(
            user=self.user6,
            game=self.game
        )

        seat1 = self.game.get_assigned_seat(player1.pk)
        seat2 = self.game.get_assigned_seat(player2.pk)
        seat3 = self.game.get_assigned_seat(player3.pk)
        seat4 = self.game.get_assigned_seat(player4.pk)
        seat5 = self.game.get_assigned_seat(player5.pk)
        seat6 = self.game.get_assigned_seat(player6.pk)
        

        
        # Verify open seats updated
        print(str(seat1), player1.user.username)
        print(str(seat2), player2.user.username)
        print(str(seat3), player3.user.username)
        print(str(seat4), player4.user.username)
        print(str(seat5), player5.user.username)
        print(str(seat6), player6.user.username)

        self.assertNotIn(str(seat1), self.game.open_seats)
        self.assertNotIn(str(seat2), self.game.open_seats)
        self.assertNotIn(str(seat3), self.game.open_seats)
        self.assertNotIn(str(seat4), self.game.open_seats)
        self.assertNotIn(str(seat5), self.game.open_seats)
        self.assertNotIn(str(seat6), self.game.open_seats)
