from channels.routing import URLRouter
from django.urls import path, include

from api.v1.chats.routing import ws_urlpatterns

ws_urlpatterns = [
    path("chat/", URLRouter(ws_urlpatterns)),
]
