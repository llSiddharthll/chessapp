from django.urls import path
from . import consumers

websocket_urlpatterns=[
    path('ws/chess/game/<int:game_id>/', consumers.ChessConsumer.as_asgi())
]