from rest_framework.permissions import IsAuthenticated

from apps.groups.models import RequestModel, BotModel
from apps.users.models import UserModel
from apps.clients.models import ClientModel
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
import api.v1.bot.serializers as local_serializers
from .auth import BotTokenAuthentication


class CreateRequestView(GenericAPIView):
    authentication_classes = [BotTokenAuthentication]
    input_serializer_class = local_serializers.CreateRequestInputSerializer
    output_serializer_class = local_serializers.CreateRequestOutputSerializer
    model = RequestModel

    def post(self, request: Request) -> Response:
        input_ser = self.input_serializer_class(data=request.data)
        input_ser.is_valid(raise_exception=True)
        bot_id = request.user.id
        telegram_id = input_ser.validated_data.get("telegram_id")
        theme = input_ser.validated_data.get("theme")
        name = input_ser.validated_data.get("name")

        bot = get_object_or_404(BotModel, id=bot_id)

        try:
            user = ClientModel.objects.get(telegram_id=telegram_id)
        except ClientModel.DoesNotExist:
            user = ClientModel.objects.create(telegram_id=telegram_id,
                                              name=name)

        request = self.model.objects.create(client_id=user.id,
                                            theme=theme, bot_id=bot.id)

        output_data = {
            "chat_id": request.id,
            "telegram_id": telegram_id
        }

        output_ser = self.output_serializer_class(output_data)

        return Response(output_ser.data, status=status.HTTP_201_CREATED)
