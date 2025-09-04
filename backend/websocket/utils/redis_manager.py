import json
import redis.asyncio as redis
from dotenv import load_dotenv
import os
from api.models import PlayerModel
load_dotenv()

REDIS_URL = os.environ.get('REDIS_URL')

async def _get_redis():
    return await redis.from_url(url=REDIS_URL, decode_responses=True)

async def set_game(game_id, state):
    '''
    Set game state in Redis
    '''
    key = f'game:{game_id}:state'
    r = await _get_redis()
    return await r.set(key, state)

async def get_game(game_id):
    '''
    Retrieve game state from Redis
    '''
    key = f'game:{game_id}:state'
    r = await _get_redis()
    return await r.get(key)

async def set_player_channel(game_id, user, channel_name):
    '''
    Sets the channel name to the seat number of the player
    '''
    seat_num = (PlayerModel.objects.get(user=user)).seat_number
    key = f'game:{game_id}:seat:{seat_num}'
    r = await _get_redis()
    return await r.set(key, channel_name)

async def get_player_channel(game_id, seat_num):
    '''
    Retrieves the channel name
    '''
    key = f'game:{game_id}:seat:{seat_num}'
    r = await _get_redis()
    return await r.get(key)