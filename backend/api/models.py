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
        '''
        Checks if the user is eligible to claim chips (1 hour cooldown)

        Return:
            -boolean: True if cooldown over else False.
        '''
        return timezone.now() >= self.chips_claimed + timedelta(hours=1)
    
    def get_claim_cooldown(self):
        '''
        Return:
            -int: the number of seconds remaining until next claim, or 0 if ready now
        '''
        next_claim_time = self.chips_claimed + timedelta(hours=1)
        remaining_time = (next_claim_time - timezone.now()).total_seconds()
        return max(0, remaining_time)

    def claim_chips(self):
        '''
        Claims hourly free chips if possible.

        Return:
            -boolean: True if chips claimed else False if claim was unsuccessful"
        '''
        with transaction.atomic():
            user = CustomUser.objects.select_for_update().get(pk=self.pk)
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
    community_cards = models.CharField(max_length=14, null=True)
    open_seats = models.CharField(default='123456', null=True)
    cards = models.CharField(max_length=157, null=True)
    game_started = models.BooleanField(default=False)

    def _seat_add_sub(self, seat, num) -> int:
        """
        Performs circular seat arithmetic; adds seat + num making sure new seat is between 1 and 6.

        Return:
            -int: an integer between 1 and 6
        """
        new_seat = seat + num
        while new_seat > 6: new_seat -= 6
        while new_seat < 1: new_seat += 6
        return new_seat
    
    def _get_seat_patterns(self, taken_seats):
        """
        Used to identify where players are sitting.

        Return:
            -int, list: the number of players sat side-by-side and the list of seats of which the players side-by-side are sitting on
        """
        side_by_side = []
        for seat in taken_seats:
            if self._seat_add_sub(seat, 1) in taken_seats or self._seat_add_sub(seat, -1) in taken_seats:
                side_by_side.append(seat)
        return len(side_by_side), side_by_side

    def _check_sides(self, seat, taken_seats):
        """
        Finds how many players are sitting next to a certain seat.

        Return:
            -int: the number of players sitting next to the seat passed in the argument
        """
        
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

        Return:
            -int: seat number or None if table is full.


        ## EASTER EGG: for who ever is reading this, quite rare that you're even seeing this since this is the 1/2 in this repo, 
        ## btw great use of free will to inspect this beautifully written code,
        ## but i do wonder why you are here, u must be extremely nosey. But either way im grateful u are here. do lmk if you find this, would be a great conversation
        '''
        with transaction.atomic():
            game = GameModel.objects.select_for_update().get(pk=self.pk)
            player = PlayerModel.objects.select_for_update().get(pk=player_pk)

            
            open_seats = [int(s) for s in game.open_seats]
            taken_seats = [seat for seat in range(1, 7) if seat not in open_seats]
            sides_count, side_seats  = self._get_seat_patterns(taken_seats) #Gets the number of players which are side by side and the seats they're sitting on.
            num_players = self.num_of_players - 1
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
            player.save(update_fields=['seat_number'])
            
            return seat
        
    def _get_centric_adjusted_seats(self, player_pk):
        '''
        Returns the seat sequence 1-6 rotated so the current player is a position 1 ensuring the user always
        sees themselves at the bottom middle seat.
        Needed so frontend UI know how to position players correctly.

        Arguments:
            -player_pk: PK number of users player model.

        Return:
            -dictionary: Containing username and chips in game of players in their respective seat or None if seat empty;
            eg {'1': {'username': 'user1', 'chips': 120}, '2': None ...}
        '''
        taken_seats = [seat for seat in range(1, 7) if str(seat) not in self.open_seats]
        all_seats = [1,2,3,4,5,6]
        player = PlayerModel.objects.get(pk=player_pk)
        player_seat = player.seat_number

        if not player_seat or not player.game:
            return None
        
        index = all_seats.index(player_seat)
        rotated_seats = all_seats[index:] + all_seats[0: index]
        player_info = {}

        for i, seat in enumerate(rotated_seats):
            if seat in taken_seats:
                seat_player = PlayerModel.objects.get(game=self.pk, seat_number=seat)
                player_info[i+1]  = {
                    'username': seat_player.user.username, 
                    'chips': seat_player.chips_in_play,
                    'id': seat_player.id,
                    'actual_seat': seat
                }
            else:
                player_info[i+1] = None

        return player_info

    def get_game_info(self, player_pk):
        '''
        Return:
            -dictioary: containing stakes, number of players, and (username + chips) for each player in-game.
        '''
        seats = self._get_centric_adjusted_seats(player_pk)
        game_info = {}
        if seats:
            game_info['small_blind'] = self.table_type.small_blind
            game_info['big_blind'] = self.table_type.big_blind
            game_info['num_of_players'] = self.num_of_players
            game_info['seats'] = seats
        return game_info
    
    def _get_next_taken_seat(self, seat):
        '''
        Takes seat number and returns the next seat that is taken by a player

        Return:
            -integer: Next seat taken, or None
        '''
        for i in range(1,7):
            seat = self._seat_add_sub(seat, 1)
            player = PlayerModel.objects.filter(game=self.id, seat_number=seat)
            if player:
                return seat
        return None
    
    def _create_deck(self):
        '''
        Creates and shuffles the deck.

        Return:
            -string: The shuffled deck of cards seperated by a comma.
        '''
        suits = ['c', 's', 'h', 'd']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        deck = []
        for value in values:
            for suit in suits:
                card = value + suit
                deck.append(card)

        random.shuffle(deck)
        deck = ','.join(deck)
        return deck

    def _deal_cards(self, game):
        '''
        Deals out hand cards to players.
        '''
        with transaction.atomic():
            players = PlayerModel.objects.select_for_update().filter(game=self.id, is_folded=False)
            deck = game.cards
            for player in players:
                player.cards = deck[0:5]
                deck = deck[6:]
                player.save()
            game.cards = deck            
    
    def start_game(self):
        '''
        Starts game; find SB,BB,Dealers and deals cards

        Return: 
            -integer: The current player to act or None if game not started.
        '''
        if self.num_of_players < 2 or self.game_started:
            return None
        
        with transaction.atomic():
            game = GameModel.objects.select_for_update().get(pk=self.pk)
            pot = PotModel.objects.create(game=game, pot_money=0)
            game.betting_stage = 0
            game.game_started = True
           
            game.dealer_position = self._get_next_taken_seat(game.dealer_position)
            sb_position = self._get_next_taken_seat(game.dealer_position)
            bb_position =  self._get_next_taken_seat(sb_amount)

            game.cards = self._create_deck()
            self._deal_cards(game)

            sb_player = PlayerModel.objects.select_for_update().get(game=game, seat_number=sb_position)
            sb_amount = min(sb_player.chips_in_play, game.table_type.small_blind)
            sb_player.chips_in_play -= sb_amount
            sb_player.current_bet = sb_amount
            sb_player.total_round_bet = sb_amount
            sb_player.save()
            pot.add_chips(sb_amount)
            pot.players.add(sb_player)

            bb_player = PlayerModel.objects.select_for_update().get(game=game, seat_number=bb_position)
            bb_amount = min(bb_player.chips_in_play, game.table_type.big_blind)
            bb_player.chips_in_play -= bb_amount
            bb_player.current_bet = bb_amount
            bb_player.total_round_bet = bb_amount
            bb_player.save()
            pot.add_chips(bb_amount)
            pot.players.add(bb_player)

            game.save()
            pot.save()
            next_player = self._get_next_taken_seat(bb_position)

            return next_player


class PlayerModel(models.Model):
    user = models.ForeignKey('api.CustomUser', on_delete=models.CASCADE)
    game = models.ForeignKey('GameModel', on_delete=models.CASCADE, null=True)
    cards = models.CharField(max_length=5, null=True)
    seat_number = models.PositiveIntegerField(null=True)
    chips_in_play = models.PositiveIntegerField(null=True)
    current_bet = models.PositiveIntegerField(null=True)
    all_in = models.BooleanField(default=False)
    is_folded = models.BooleanField(default=False)
    had_acted = models.BooleanField(default=False)
    total_round_bet = models.PositiveIntegerField(default=0)

    def join_game(self, game, user_pk, buy_in):
        '''
        Assigns the game to the player and updates chips after buy-in.

        Return:
            -boolean: False if user is already in a game or if user has insufficient chips else True.
        '''
        with transaction.atomic():
            user = CustomUser.objects.select_for_update().get(pk=user_pk)
            player = PlayerModel.objects.select_for_update().get(pk=self.pk)

            if player.game:
                return False
            
            if user.chips < buy_in:
                return False

            user.chips -= buy_in
            player.game = game
            player.chips_in_play = buy_in

            user.save(update_fields=['chips'])
            player.save(update_fields=['chips_in_play', 'game'])
            return True

    def leave_game(self, user_pk, game_pk):
        '''
        Player leaves game by updates/resetting nessecary fields in user, player and game models.
        '''
        with transaction.atomic():
            player = PlayerModel.objects.select_for_update().get(pk=user_pk)
            user = CustomUser.objects.select_for_update().get(pk=user_pk)
            game = GameModel.objects.select_for_update().get(pk=game_pk)

            user.chips += player.chips_in_play

            current_seats = [s for s in game.open_seats]
            current_seats.append(str(player.seat_number))
            game.open_seats = ''.join(sorted(current_seats))
            game.num_of_players -= 1

            player.chips_in_play = 0
            player.seat_number = None
            player.game = None
            player.is_folded = False
            player.all_in = False
            player.current_bet = 0
            player.total_round_bet = 0

            user.save(update_fields=['chips'])
            game.save(update_fields=['open_seats', 'num_of_players'])
            player.save(update_fields=['chips_in_play', 'seat_number', 'game', 'is_folded', 'all_in', 'current_bet', 'total_round_bet'])