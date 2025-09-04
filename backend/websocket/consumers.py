import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils.game import *

class PokerGameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        self.user = await get_user(self.token)
        self.game = await user_in_game(self.user)
        if self.user and self.game:
            self.room_group_name = f'poker_{self.game.id}'
            await self.accept()

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'player_joined',
                'user_id': self.user.id
            })
            await set_player_channel(self.game.id, self.user, self.channel_name)

            channel_name = await start_game(self.game)
            if channel_name:
                await self.channel_layer.send(channel_name, {'type': 'player_to_act'})
        else:
            await self.close()
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

    async def player_joined(self, event):
        game_info = await get_game_info(self.user) 
        if event.get('user_id') == self.user.id:
            await self.send(text_data=json.dumps({'event': 'game_joined', 'data': game_info}))
        else:
            await self.send(text_data=json.dumps({'event': 'player_joined', 'data': game_info}))

    async def player_left(self, event):
        user_id = event.get('user_id')
        if user_id == self.user.id:
            leave_game(self.user)
            await self.send(text_data=json.dumps({'event': 'game_leave'}))
        else:
            await self.send(text_data=json.dumps({'event': 'player_left', 'user_id': user_id}))

    async def player_to_act(self, event):
        await self.send(text_data=json.dumps({'event': 'Your turn to act'}))