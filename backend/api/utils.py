from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from .models import GameModel

def get_jwt_tokens(user):
    '''Returns a refresh and access token for the user'''
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)

def game_matchmaking():
    '''Returns a suitable non-full game the user can join or None if all games are full.'''
    with transaction.atomic():
        game = GameModel.objects.select_for_update().filter(num_of_players__lt=6).order_by('num_of_players', 'created_at').first()
       
        if not game:
            return None
        elif game.num_of_players == 6:
            return None
        
        game.num_of_players += 1
        game.save(update_fields=['num_of_players'])
        return game
        