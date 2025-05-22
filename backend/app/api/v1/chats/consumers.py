import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.groups.models import MessageModel, RequestModel, GroupModel


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_id = None
        self.group_name = None
        self.user = None

    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f"chat_{self.chat_id}"
        self.user = self.scope.get("user")
        if not await self.has_access():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        text = data.get('text')
        user = self.scope['user']
        if not text or not user:
            return
        message = await MessageModel.objects.acreate(
            request_id=self.chat_id,
            user_id=user.id,
            text=text,
        )

        await self.channel_layer.group_send(
            f"chat_{self.chat_id}",
            {
                'type': 'chat_message',
                'message': {
                    'id': str(message.id),
                    'user_id': str(user.id),
                    'user_type': user.type,
                    'text': message.text,
                    'sended': str(message.sended)
                }
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @sync_to_async
    def has_access(self):
        if self.user and self.user.type == "agent":
            bot = RequestModel.objects.get(id=self.chat_id).bot
            return GroupModel.objects.filter(
                bots__id=bot.id,
                agents__id=self.user.id
            ).exists()
        elif self.user.type == "client":
            return RequestModel.objects.filter(id=self.chat_id, client_id=self.user.id).exists()
