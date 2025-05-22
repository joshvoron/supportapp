import re
import base64
import hmac
import hashlib
import uuid
from urllib.parse import parse_qs

import jwt
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import UserModel
from apps.groups.models import BotModel, RequestModel


@database_sync_to_async
def get_user_from_jwt(token: str) -> UserModel:
    """Authenticate a user via JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return UserModel.objects.get(id=payload["user_id"])
    except (jwt.DecodeError, jwt.ExpiredSignatureError, UserModel.DoesNotExist):
        raise AuthenticationFailed("Invalid or expired token")


@database_sync_to_async
def get_verified_user(chat_id: str, token: str) -> str | None:
    print(chat_id)
    try:
        request = (
            RequestModel.objects
            .select_related('client', 'bot')
            .get(id=chat_id)
        )
    except RequestModel.DoesNotExist:
        return None

    if not _verify_secure_token(request.client.telegram_id, request.bot.secret_key, token):
        raise AuthenticationFailed("Invalid bot credentials")

    return UserModel.objects.get(id=request.client.id)


def _verify_secure_token(user_id: str, secret_key: uuid.uuid4, token: str) -> bool:
    """Verify HMAC-based secure token for bot authentication."""
    expected = hmac.new(
        str(secret_key).encode(),
        user_id.encode(),
        hashlib.sha256
    ).digest()
    try:
        decoded = base64.urlsafe_b64decode(token.encode())
        print(decoded)
        print(expected)
    except (TypeError, ValueError):
        return False

    return hmac.compare_digest(decoded, expected)


class AuthMiddleware(BaseMiddleware):
    """
    Custom middleware for Channels that authenticates either a user via JWT
    or a bot via secure key per chat.
    """

    async def __call__(self, scope, receive, send):
        # Extract chat_id from path, e.g. /ws/chat/{chat_id}/
        path = scope.get('path', '')
        match = re.search(r'/chat/(?P<chat_id>[0-9a-f\-]+)/', path)
        if not match:
            await self._close_connection(send, "Chat ID is missing or invalid")
            return

        chat_id = match.group('chat_id')
        scope['chat_id'] = chat_id

        # Parse query parameters
        query_params = parse_qs(scope.get('query_string', b'').decode())
        token = query_params.get('token')
        secure_key = query_params.get('secure_key')

        try:
            if token:
                scope['user'] = await get_user_from_jwt(token[0])
            elif secure_key:
                scope['user'] = await get_verified_user(chat_id, secure_key[0], )
            else:
                raise AuthenticationFailed("Authentication credentials not provided")
        except AuthenticationFailed as exc:
            await self._close_connection(send, str(exc))
            return

        return await super().__call__(scope, receive, send)

    async def _close_connection(self, send, reason: str, code: int = 4001):
        """Helper to close WebSocket connection with reason."""
        await send({
            "type": "websocket.close",
            "code": code,
            "reason": reason,
        })
