from django.urls import path

from . import solo_consumers, multi_consumers, view_consumers

websocket_urlpatterns = [
    path('ws/solo/<int:player_id>/', solo_consumers.ChatConsumer),
    path('ws/multi/<int:room_id>/', multi_consumers.ChatConsumer),
    path('ws/view/<int:room_id>/', view_consumers.ChatConsumer),
]
