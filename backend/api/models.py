from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random

stage_choices = [
    (0, 'Pre-flop'),
    (1, 'Flop'),
    (2, 'Turn'),
    (3, 'River'),
    (4, 'Showdown'),
    (5, 'New Round')
]

CHIP_CLAIM_AMOUNT = 500

def get_default_chips_claimed():
    """Returns timezone.now() - 1 hour (for immediate first claim)"""
    return timezone.now() - timedelta(hours=1)


class CustomUser(AbstractUser):
    chips = models.PositiveIntegerField(default=1000)
    chips_claimed = models.DateTimeField(default=get_default_chips_claimed)

    def __str__(self):
        return self.username
    
    def can_claim_chips(self):
        '''Checks if the user is eligible to claim chips (1 hour cooldown)'''
        return timezone.now() >= self.chips_claimed + timedelta(hours=1)
    
    def get_claim_cooldown(self):
        '''Returns seconds remaining until next claim, or 0 if ready'''
        next_claim_time = self.chips_claimed + timedelta(hours=1)
        remaining_time = (next_claim_time - timezone.now()).total_seconds()
        return max(0, remaining_time)

    def claim_chips(self):
        '''Claims hourly free chips if possible'''
        with transaction.atomic():
            user = CustomUser.objects.select_for_update(of=('chips', 'chips_claimed')).get(pk=self.pk)
            if user.can_claim_chips():
                user.chips += CHIP_CLAIM_AMOUNT
                user.chips_claimed = timezone.now()
                user.save(update_fields=['chips', 'chips_claimed'])
                return True
            return False

class TableTypeModel(models.Model):
    big_blind = models.PositiveIntegerField()
    small_blind = models.PositiveIntegerField()
    min_buy_in = models.PositiveIntegerField()
    max_buy_in = models.PositiveIntegerField()

class PotModel(models.Model):
    game = models.ForeignKey('GameModel', on_delete=models.CASCADE)
    players = models.ManyToManyField('PlayerModel', related_name='pots')
    pot_money = models.PositiveIntegerField(default=0)
    closed = models.BooleanField(default=False)

    def add_chips(self, amount):
        '''Add chips to this pot'''
        self.pot_money = models.F('pot_money') + amount
        self.save(update_fields=['pot_money'])

class GameModel(models.Model):
    table_type = models.ForeignKey('TableTypeModel', on_delete=models.CASCADE)
    current_turn = models.ForeignKey('PlayerModel', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    private = models.BooleanField(default=False)
    code = models.CharField(max_length=8, null=True)
    num_of_players = models.PositiveIntegerField(default=0, max_length=6)
    betting_stage = models.PositiveSmallIntegerField(choices=stage_choices, default=0)
    dealer_position = models.PositiveIntegerField(default=0)
    community_cards = models.CharField(max_length=14, blank=True)
    open_seats = models.CharField(default='123456')

    def _seat_add_sub(self, seat, num) -> int:
        """Performs circular seat arithmetic"""
        new_seat = seat + num
        while new_seat > 6: new_seat -= 6
        while new_seat < 1: new_seat += 6
        return new_seat
    
    def _get_seat_patterns(self, taken_seats):
            """Identifies seating patterns"""
            side_by_side = []
            for seat in taken_seats:
                if self._seat_add_sub(seat, 1) in taken_seats or self._seat_add_sub(seat, -1) in taken_seats:
                    side_by_side.append(seat)
            return len(side_by_side), side_by_side

    def _check_sides(self, seat, taken_seats):
                count = 0
                next = self._seat_add_sub(seat, 1)
                if next in taken_seats:
                    count += 1
                previous = self._seat_add_sub(seat, -1)
                if previous in taken_seats:
                    count += 1
                return count
    
    def get_assigned_seat(self, player_pk):
        '''
        Assigns optimal and logical seat based on the current player distribution.
        Returns seat number or None if table is full.

        ## EASTER EGG: for who ever is reading this, quite rare that you're even seeing this since this is the 1/2 in this repo, 
        ## btw great use of free will to inspect this beautifully written code,
        ## but i do wonder why you are here, u must be extremely nosey. But either way im grateful u are here. do lmk if you find this, would be a great conversation
        '''
        if self.num_of_players == 6:
            return None
        
        with transaction.atomic():
            game = GameModel.objects.select_for_update(of=('open_seats',)).get(pk=self.pk)
            player = PlayerModel.objects.select_for_update(of=('seat_number',)).get(pk=player_pk)

            taken_seats = [p.seat_number for p in game.playermodel_set.all()]
            open_seats = [int(s) for s in game.open_seats]
            sides_count, side_seats  = self._get_seat_patterns(taken_seats) #Gets the number of players which are side by side and the seats they're sitting on.
            num_players = self.num_of_players
            seat = None

            if num_players == 0:
                seat = 1

            elif num_players == 1:
                seat = self._seat_add_sub(taken_seats[0], 3)

            elif num_players == 2:

                if sides_count == 2: #If 2 players are sitting side-by-side, it picks a seat opposite to one of the two players.
                    seat = self._seat_add_sub(random.choices(taken_seats), 3)
                else: #If the 2 players are sitting together with 1 free seat between them, then pick a seat so it creates a triangle.
                    #If the 2 players are sitting opposite each other, it doesnt matter so it also performs this assignment.
                    max_seat = max(taken_seats)
                    seat = self._seat_add_sub(max_seat, 2)
                    if seat not in open_seats:
                        seat = self._seat_add_sub(max_seat, -2)
            elif num_players == 3:
                if sides_count == 3: #If all players are setting side-by-side each other, picks the seat opposite to the middle player
                    max_seat = max(taken_seats)
                    seat = self._seat_add_sub(max_seat, 2)
                    if seat not in open_seats:
                        seat = self._seat_add_sub(max_seat, -2)
                elif sides_count == 2: #If 2 players are side-by-side with an lone player, then picks seat next to lone pla0yer.
                    lone_player = [s for s in taken_seats if s not in side_seats][0]
                    seat = self._seat_add_sub(lone_player, 1)
                    if self._check_sides(seat, taken_seats) == 2:
                        seat = self._seat_add_sub(lone_player, -1)
                else:
                    seat = random.choice(open_seats)
            else:
                seat = random.choice(open_seats)

            if seat not in open_seats or seat == None: #Safe fallback in-case it all goes wrong, ofc this will NEVER happens, on my soul.
                seat = open_seats[0]
            
            self.open_seats = self.open_seats.replace(str(seat), '')
            self.save(update_fields=['open_seats'])

            player.seat_number = seat
            player.save(updated_fields=['seat_number'])
            
            return seat

class PlayerModel(models.Model):
    user = models.ForeignKey('api.CustomUser', on_delete=models.CASCADE)
    game = models.ForeignKey('GameModel', on_delete=models.CASCADE, null=True)
    cards = models.CharField(max_length=5, null=True)
    seat_number = models.PositiveIntegerField(null=True)
    chip_in_play = models.PositiveIntegerField(null=True)
    current_bet = models.PositiveIntegerField(null=True)
    all_in = models.BooleanField(default=False)
    is_folded = models.BooleanField(default=False)
    had_acted = models.BooleanField(default=False)
    total_round_bet = models.PositiveIntegerField(default=0)

    def join_game(self, game, user_pk, buy_in):
        '''
        Assigns the game to the player and updates chips after buy-in.
        Returns False if user is already in a game or if user has insufficient chips.
        '''
        with transaction.atomic():
            user = CustomUser.objects.select_for_update(of=('chips',)).get(pk=user_pk)
            player = PlayerModel.objects.select_for_update(of=('chips_in_play', 'game')).get(pk=self.pk)

            if player.game:
                return False
            
            if user.chips < buy_in:
                return False

            user.chips -= buy_in
            player.game = game
            player.chip_in_play = buy_in

            user.save(update_fields=['chips'])
            player.save(update_fields=['chips_in_play', 'game'])

    def leave_game(self, user_pk, game_pk):
        with transaction.atomic():
            player = PlayerModel.objects.select_for_update().get(pk=user_pk)
            user = CustomUser.objects.select_for_update().get(pk=user.id)
            game = GameModel.objects.select_for_update(of=('open_seats', 'num_of_players')).get(pk=game_pk)

            user.chips += player.chip_in_play

            current_seats = set(game.open_seats).add(str(player.seat_number))
            game.open_seats = ''.join(sorted(current_seats))
            game.num_of_players -= 1

            player.chip_in_play = 0
            player.seat_number = None
            player.game = None
            player.is_folded = False
            player.all_in = False
            player.current_bet = 0
            player.total_round_bet = 0

            user.save(update_fields=['chips'])
            game.save(updated_fields=['open_seats', 'num_of_players'])
            player.save(update_fields=['chips_in_play', 'seat_number', 'game', 'is_folded', 'all_in', 'current_bet', 'total_round_bet'])