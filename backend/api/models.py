from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

stage_choices = [
    (0, 'Pre-flop'),
    (1, 'Flop'),
    (2, 'Turn'),
    (3, 'River'),
    (4, 'Showdown')
]


class CustomUser(AbstractUser):
    chips = models.PositiveIntegerField(default=1000)

    def __str__(self):
        return self.username


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
    current_turn = models.ForeignKey('PlayerModel', on_delete=models.CASCADE)
    private = models.BooleanField(default=False)
    is_full = models.BooleanField(default=False)
    betting_stage = models.PositiveSmallIntegerField(choices=stage_choices,default=0)


class PlayerModel(models.Model):
    user = models.ForeignKey('api.CustomUser', on_delete=models.CASCADE)
    game = models.ForeignKey('GameModel', on_delete=models.CASCADE, null=True)
    chips_last_claimed = models.DateTimeField()
    seat_number = models.PositiveIntegerField(null=True)
    chips = models.PositiveIntegerField(default=500)
    chip_in_play = models.PositiveIntegerField(null=True)
    current_bet = models.PositiveIntegerField(null=True)
    all_in = models.BooleanField(default=False)
    is_folded = models.BooleanField(default=False)
    had_acted = models.BooleanField(default=False)
    total_round_bet = models.PositiveIntegerField(default=0)
