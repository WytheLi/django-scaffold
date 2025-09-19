import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Conversation
from .models import Message

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # 验证用户是否属于该对话
        # 异步调用时传入 primitive types，避免跨线程传 model 实例
        if await self.is_participant(self.conversation_id, self.user.id):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # 保存消息到数据库
        message_obj = await self.save_message(self.conversation_id, self.user.id, message)

        # 发送消息到群组
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": {
                    "id": message_obj.id,
                    "sender": {"id": self.user.id, "username": self.user.username},
                    "content": message_obj.content,
                    "timestamp": message_obj.timestamp.isoformat(),
                    "is_read": False,
                },
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def is_participant(self, conversation_id: str, user_id: int):
        return Conversation.objects.filter(id=conversation_id, participants__id=user_id).exists()

    @database_sync_to_async
    def save_message(self, conversation_id: str, user_id: int, content: str):
        conversation = Conversation.objects.select_related().get(id=conversation_id)
        message = Message.objects.create(conversation=conversation, sender_id=user_id, content=content)
        return message
