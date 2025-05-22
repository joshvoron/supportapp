from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from apps.groups.models import RequestModel, BotModel, GroupModel, MessageModel

import api.v1.chats.serializers as local_serializers
from api.v1.settings.serializers import ObjectSerializer


# Get stats
class ChatListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = local_serializers.ChatListSerializer
    model = GroupModel

    def post(self, request: Request):
        group_id = request.data.get("group_id")
        if not group_id:
            return Response({"error": "group_id is missing or invalid"})
        try:
            group = self.model.objects.get(id=group_id, agents__id=request.user.id)
        except self.model.DoesNotExist:
            return Response({'error': "Model doesn't exist"},
                            status=404)

        bot_list = group.bots.all()
        requests = RequestModel.objects.filter(bot__in=bot_list)
        payload = [
            {
                "bot_name": item.name,
                "chats": [
                    {
                        "id": chat.id,
                        "theme": chat.theme,
                        "last_msg": (MessageModel.objects.filter(
                            request_id=chat.id).order_by('-sended').first(
                        ) or MessageModel(text="No messages")).text
                    }
                    for chat in requests.filter(bot_id=item.id)
                ]
            } for item in bot_list
        ]

        serializer = self.get_serializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=200)


class GroupListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ObjectSerializer
    model = GroupModel

    def get(self, request: Request):
        qs = self.model.objects.filter(agents__id=request.user.id)
        payload = [
            {
                "name": item.name,
                "id": item.id,
            }
            for item in qs
        ]
        serializer = self.get_serializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=200)


class ChatMessageList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    input_serializer_class = local_serializers.ChatMessagesInputSerializer
    output_serializer_class = local_serializers.MessagesListSerializer
    model = MessageModel

    def post(self, request):
        input_ser = self.input_serializer_class(data=request.data)
        input_ser.is_valid(raise_exception=True)
        chat_id = input_ser.validated_data.get("chat_id")
        message_id = input_ser.validated_data.get("message_id")
        include_info = input_ser.validated_data.get("include_info")

        qs = self.model.objects.filter(request_id=chat_id).order_by(
            "-sended")

        if message_id:
            last_msg = get_object_or_404(self.model, id=message_id)
            qs = qs.filter(sended__lt=last_msg.sended)

        messages = list(qs[:100])
        messages_qs = list(reversed(messages))

        chat_info = None
        if include_info:
            req = get_object_or_404(RequestModel, id=chat_id)
            chat_info = {
                "id": req.id,
                "client_name": req.client.name,
                "created": req.created,
                "is_solved": req.is_solved,
                "theme": req.theme,
                "solved_by": req.solved_by.name if req.solved_by else None,
            }

        output_data = {
            "chat_info": chat_info,
            "messages": messages_qs
        }

        output_ser = self.output_serializer_class(output_data)
        return Response(output_ser.data, status=status.HTTP_200_OK)
