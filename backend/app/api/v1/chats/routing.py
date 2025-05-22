from django.urls import re_path

from . import consumers

ws_urlpatterns = [
    re_path("(?P<chat_id>[^/]+)/$", consumers.ChatConsumer.as_asgi()),
]
