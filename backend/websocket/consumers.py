import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import *

class PokerGameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        self.user = await get_user(self.token)
        game = await user_in_game(self.user)
        if self.user and game:
            self.room_group_name = f'poker_{game.id}'
            await self.accept()

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'player_joined',
                'user_id': self.user.id
            })
        else:
            await self.close()
    
    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)

    async def player_joined(self, event):
        game_info = await get_game_info(self.user) 
        if event.get('user_id') == self.user.id:
            await self.send(text_data=json.dumps({'event': 'game_joined', 'data': game_info}))
        else:
            await self.send(text_data=json.dumps({'event': 'player_joined', 'data': game_info}))
    
                