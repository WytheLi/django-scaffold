from account.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""

    password_confirm = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "mobile", "password", "password_confirm")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        # 验证密码确认
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("两次密码输入不一致")

        return attrs

    def create(self, validated_data):
        # 创建用户
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            mobile=validated_data.get("mobile", ""),
            password=validated_data["password"],
        )
        return user
