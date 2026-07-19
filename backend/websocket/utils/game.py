from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from api.models import PlayerModel
from .redis_manager import get_player_channel


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
    # TO-DO: Fix this and then replace the LeaveGame in views.py
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
    Starts game.

    Return:
        -tuple: (channel_name, seat_num) of the player to act, or (None, None)
            if the game couldn't start.

    ## EASTER EGG: for who ever is reading this.
    ## btw great use of free will to inspect this beautifully written code,
    ## but i do wonder why you are here, you must be extremely nosey or a hiring manager
    ## But either way im grateful u are here. do lmk if you find this,
    ## would be a great conversation starter
    ## PLS HIRE ME IF YOU ARE A HIRING MANAGER OR INTERVIEWER OR ANYONE THAT CAN GET ME A JOB
    '''
    seat_num = await sync_to_async(game.start_game)()
    if seat_num:
        channel_name = await get_player_channel(game.id, seat_num)
        return channel_name, seat_num
    return None, None
