import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PokerGameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'hello_message',
            'message': 'you have recived this'
        }))
    
    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        
        print(f"Received message: {message}")
        
        await self.send(text_data=json.dumps({
            'type': 'echo',
            'message': f'Server received: {message}'
        }))