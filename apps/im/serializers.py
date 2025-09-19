from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Conversation
from .models import Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "content", "timestamp", "is_read"]
        read_only_fields = ["id", "sender", "timestamp"]

    def get_is_read(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.is_read_by(request.user)
        return False


class ConversationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    participants = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False, help_text="用户 ID 列表"
    )
    is_group = serializers.BooleanField(default=False)

    def validate_participants(self, value):
        # remove duplicates (PrimaryKeyRelatedField 已保证唯一对象，但序列里仍可能重复)
        unique = []
        ids = set()
        for u in value:
            if u.pk not in ids:
                ids.add(u.pk)
                unique.append(u)
        return unique

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["view"].request.user
        conversation = Conversation.objects.create(
            name=validated_data.get("name", ""),
            is_group=validated_data.get("is_group", False),
        )

        # participants 是 User 实例列表（可能为空）
        participants = validated_data.get("participants", [])
        # 确保创建者在 participants 中
        if user not in participants:
            # add accepts model instances or ids; 使用实例更明确
            conversation.participants.add(user)
            if participants:
                conversation.participants.add(*participants)
        else:
            # 用户已在 participants 列表中
            conversation.participants.add(*participants)

        # 立即刷新 conversation（以便拿到 m2m 之后的状态）
        conversation.refresh_from_db()
        return conversation


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "name", "participants", "is_group", "created_at", "last_message", "unread_count"]

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.messages.exclude(read_by=request.user).count()
        return 0
