import logging

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token):
    try:
        access = AccessToken(token)
        user_id = access["user_id"]
        return User.objects.get(pk=user_id)
    except Exception:
        logger.warning("WebSocket JWT authentication failed")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token = None

        for part in query_string.split("&"):
            if part.startswith("token="):
                token = part.split("=", 1)[1]
                break

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
