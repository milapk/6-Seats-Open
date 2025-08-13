from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

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
    num_of_players = models.PositiveIntegerField(default=0)
    betting_stage = models.PositiveSmallIntegerField(choices=stage_choices, default=0)
    dealer_position = models.PositiveIntegerField(default=0)
    community_cards = models.CharField(max_length=14, blank=True)
    open_seats = models.CharField(default='123456')


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
