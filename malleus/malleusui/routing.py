from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/console/<str:lab_id>/<str:instance_name>/", consumers.WebsocketProxyConsumer.as_asgi()),
]