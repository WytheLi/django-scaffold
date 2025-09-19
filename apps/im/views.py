from datetime import timedelta

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.response import StandardResponse
from core.stat_code import StatCode

from .models import Conversation
from .models import Message
from .serializers import ConversationCreateSerializer
from .serializers import ConversationSerializer
from .serializers import MessageSerializer


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="获取当前用户参与的所有对话列表",
        description="查询参与的所有对话最近一条消息",
        tags=[_("IM")],
    )
    def get(self, request):
        """
        获取当前用户参与的所有对话列表（查询参与的所有对话最近一条消息）
        :param request:
        :return:
        """
        conversations = Conversation.objects.filter(participants=request.user)
        serializer = ConversationSerializer(conversations, many=True, context={"request": request})
        return StandardResponse(StatCode.SUCCESS, data=serializer.data)


class ConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request, "format": self.format_kwarg, "view": self}

    @extend_schema(
        request=ConversationCreateSerializer,
        summary="创建会话",
        description="创建会话。若为私聊，存在的会话直接返回会话ID",
        tags=[_("IM")],
    )
    def post(self, request, *args, **kwargs):
        """
        创建会话。请求体示例：
        {
          "name": "Project Chat",
          "participants": [2, 3],   # 用户 id 列表（不需要包含创建者）
          "is_group": true
        }
        :param request:
        :param args:
        :param kwargs:
        :return: {
          "conversation_id": "uuid-string",
          "name": "...",
          "participants": [1,2,3]
        }
        """
        kwargs.setdefault("context", self.get_serializer_context())
        serializer = ConversationCreateSerializer(data=request.data, **kwargs)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()

        data = {
            "conversation_id": str(conversation.id),
            "name": conversation.name,
            "is_group": conversation.is_group,
            "participants": [u.pk for u in conversation.participants.all()],
        }
        return StandardResponse(StatCode.SUCCESS, data=data)


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="获取特定对话信息",
        description="查询最近一条对话消息",
        tags=[_("IM")],
    )
    def get(self, request, conversation_id):
        """
        获取特定对话信息（查询最近一条消息）
        :param request:
        :param conversation_id:
        :return:
        """
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

        serializer = ConversationSerializer(conversation, context={"request": request})
        return StandardResponse(StatCode.SUCCESS, data=serializer.data)


class MessageHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="获取特定对话的历史消息",
        description="获取特定对话的指定时间区间内的历史消息",
        tags=[_("IM")],
    )
    def get(self, request, conversation_id):
        """
        获取特定对话的历史消息
        :param request:
        :param conversation_id:
        :return:
        """
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

        # 获取一周内的消息
        one_week_ago = timezone.now() - timedelta(days=settings.MESSAGE_RETENTION_DAYS)
        messages = conversation.messages.filter(timestamp__gte=one_week_ago)

        serializer = MessageSerializer(messages, many=True, context={"request": request})
        return StandardResponse(StatCode.SUCCESS, data=serializer.data)


class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="message_id", type=str, location="path", required=True, description="消息 ID")
        ],
        summary="标记单条消息为已读",
        description="标记单条消息为已读",
        tags=[_("IM")],
    )
    def post(self, request, message_id):
        """
        标记单条消息为已读
        :param request:
        :param message_id:
        :return:
        """
        message = get_object_or_404(Message, id=message_id)

        # 验证用户是否有权限访问这条消息
        if request.user not in message.conversation.participants.all():
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        marked = message.mark_as_read(request.user)
        if marked:
            return StandardResponse(StatCode.SUCCESS, _("marked as read"))
        else:
            return StandardResponse(StatCode.SUCCESS, _("already read"))


class MarkConversationAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="conversation_id", type=str, location="path", required=True, description="对话ID")
        ],
        summary="将特定对话中的所有消息标记为已读",
        description="将特定对话中的所有消息标记为已读",
        tags=[_("IM")],
    )
    def post(self, request, conversation_id):
        """
        将特定对话中的所有消息标记为已读
        :param request:
        :param conversation_id:
        :return:
        """
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

        # 标记所有未读消息为已读
        unread_messages = conversation.messages.exclude(read_by=request.user)
        for message in unread_messages:
            message.mark_as_read(request.user)

        return StandardResponse(StatCode.SUCCESS, _("all messages marked as read"))


class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="conversation_id", type=str, location="path", required=False, description="对话ID")
        ],
        summary="将特定对话中的所有消息标记为已读",
        description="将特定对话中的所有消息标记为已读",
        tags=[_("IM")],
    )
    def get(self, request, conversation_id=None):
        """
        获取当前用户在所有对话/特定对话中的未读消息数量
        :param request:
        :param conversation_id:
        :return:
        """
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
            count = conversation.messages.exclude(read_by=request.user).count()
        else:
            # 所有对话的未读消息总数
            conversations = Conversation.objects.filter(participants=request.user)
            count = 0
            for conversation in conversations:
                count += conversation.messages.exclude(read_by=request.user).count()

        return StandardResponse(StatCode.SUCCESS, data={"unread_count": count})
