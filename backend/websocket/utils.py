from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from api.models import PlayerModel, GameModel

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