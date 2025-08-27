from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/poker/<path:token>/', consumers.PokerGameConsumer.as_asgi())
]