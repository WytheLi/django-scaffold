from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from utils.jwt_handler import jwt_decode_handler
from utils.jwt_handler import jwt_get_user_id_from_payload_handler


class JWTAuthMiddleware:
    """
    ASGI middleware for channels that authenticates users by JWT.
    It supports:
      - ?token=<access_token> in query string
      - token sent in Sec-WebSocket-Protocol header (common when using browser WebSocket protocols param)
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # 默认匿名
        scope["user"] = AnonymousUser()

        # 先从 query_string 里找
        query_string = scope.get("query_string", b"").decode()
        qs = parse_qs(query_string)
        token = None
        if "token" in qs:
            token = qs["token"][0]

        # 如果没有，再从 headers 的 sec-websocket-protocol 读取
        if not token:
            headers = dict(scope.get("headers", []))
            proto = headers.get(b"sec-websocket-protocol")
            if proto:
                token = proto.decode()

        if token:
            payload = jwt_decode_handler(token)
            user_id = jwt_get_user_id_from_payload_handler(payload)

            user = await self._get_user(user_id)
            if user:
                scope["user"] = user

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def _get_user(self, user_id):
        """
        根据user_id获取用户
        :param user_id:
        :return:
        """
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            return None
