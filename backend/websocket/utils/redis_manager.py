import json
import redis.asyncio as redis
from dotenv import load_dotenv
import os
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