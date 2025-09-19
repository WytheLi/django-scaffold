import uuid

from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel

User = get_user_model()


class Conversation(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=255, verbose_name="名称")
    participants = models.ManyToManyField(User, related_name="conversations", verbose_name="参与者")
    is_group = models.BooleanField(default=False, verbose_name="是否为群聊")

    class Meta:
        verbose_name = "对话"
        verbose_name_plural = "对话"

    def __str__(self):
        return self.name


class Message(BaseModel):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE, verbose_name="对话"
    )
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE, verbose_name="发送者")
    content = models.TextField(verbose_name="内容")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="时间戳")
    read_by = models.ManyToManyField(User, related_name="read_messages", blank=True, verbose_name="已读用户")

    class Meta:
        verbose_name = "消息"
        verbose_name_plural = "消息"

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"

    def is_read_by(self, user):
        return self.read_by.filter(id=user.id).exists()

    def mark_as_read(self, user):
        if not self.is_read_by(user):
            self.read_by.add(user)
            return True
        return False
