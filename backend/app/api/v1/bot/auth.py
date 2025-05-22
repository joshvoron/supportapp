from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from apps.groups.models import BotModel


class BotTokenAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        token = request.headers.get("X-Bot-Token")
        if not token:
            return None
        try:
            bot = BotModel.objects.get(secret_key=token)
        except BotModel.DoesNotExist:
            raise AuthenticationFailed("Invalid bot token")

        return bot, None
