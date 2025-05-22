from channels.routing import URLRouter
from django.urls import path, include

from api.v1.routing import ws_urlpatterns

ws_urlpatterns = [
    path("ws/", URLRouter(ws_urlpatterns)),
]
