from asgiref.sync import sync_to_async
import redis.asyncio as redis
from dotenv import load_dotenv
import os
import time
from api.models import PlayerModel
load_dotenv()

REDIS_URL = os.environ.get('REDIS_URL')


async def _get_redis():
    return await redis.from_url(url=REDIS_URL, decode_responses=True)


async def set_game(game_id, state):
    '''
    Set game state in Redis
    '''
    key = f'game#{game_id}:state'
    r = await _get_redis()
    return await r.set(key, state)


async def get_game(game_id):
    '''
    Retrieve game state from Redis
    '''
    key = f'game#{game_id}:state'
    r = await _get_redis()
    return await r.get(key)


async def set_player_channel(game_id, user, channel_name):
    '''
    Sets the channel name to the seat number of the player
    '''
    seat_num = await sync_to_async(PlayerModel.objects.get)(user=user)
    seat_num = seat_num.seat_number
    key = f'game#{game_id}:seat#{seat_num}'
    r = await _get_redis()
    return await r.set(key, channel_name)


async def get_player_channel(game_id, seat_num):
    '''
    Retrieves the channel name
    '''
    key = f'game#{game_id}:seat#{seat_num}'
    r = await _get_redis()
    return await r.get(key)


async def set_player_turn_deadline(game_id, seat_num):
    '''
    Sets the player that is currently acting; gives them a 2 minute timer to act

    Return:
        The deadline as a unix timestamp (float, seconds)
    '''
    key = f'game#{game_id}:seat#{seat_num}:to.act'
    deadline = time.time() + 120
    r = await _get_redis()
    await r.hset(key, mapping={'player_acted': '0', 'deadline': deadline})
    await r.expire(key, 120)
    return deadline


async def get_player_turn_deadline(game_id, seat_num):
    '''
    Retrieves the current acting player's deadline info

    Return:
        dict with 'player_acted' (bool) and 'deadline' (float unix timestamp),
        or None if no deadline is set (expired or never set)
    '''
    key = f'game#{game_id}:seat#{seat_num}:to.act'
    r = await _get_redis()
    value = await r.hgetall(key)
    if not value:
        return None
    return {
        'player_acted': value['player_acted'] == '1',
        'deadline': float(value['deadline']),
    }


async def clear_player_turn_deadline(game_id, seat_num):
    '''
    Marks the player as having acted, clearing their turn timer
    '''
    key = f'game#{game_id}:seat#{seat_num}:to.act'
    r = await _get_redis()
    return await r.delete(key)