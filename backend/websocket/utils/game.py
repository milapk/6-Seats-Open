from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from api.models import PlayerModel, GameModel
from .redis_manager import *

@database_sync_to_async
def get_user(token):
    '''
    Return:
        -user: Returns user object if the token is valid, else None
    '''
    auth = JWTAuthentication()
    try:
        token = auth.get_validated_token(token)
        return auth.get_user(validated_token=token)
    except InvalidToken:
        return None
    
@database_sync_to_async
def user_in_game(user):
    '''
    Return:
        -game: Returns game object if user is in-game, else None
    '''
    player = PlayerModel.objects.get(user=user)
    if player.game:
        return player.game
    return None

@database_sync_to_async
def get_game_info(user):
    '''
    Return:
        -dictionary: containing game info or None
    '''
    player = PlayerModel.objects.get(user=user)
    game = player.game
    if game:
        return game.get_game_info(player.pk)
    return None

@database_sync_to_async
def leave_game(user):
    '''
    Leaves game

    Return:
        -boolean: True if successful, else False
    '''
    player = PlayerModel.objects.get(user=user)
    game = player.game
    if game:
        player.leave_game
        return True
    return False

async def start_game(game):
    '''
    Starts game and Returns channel name of the player to act or None if game could'nt start.
    '''
    seat_num = await sync_to_async(game.start_game)()
    if seat_num:
        return await get_player_channel(game.id, seat_num)
    return None