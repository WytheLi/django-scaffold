import uuid

from account.models import User
from django.conf import settings
from django.forms import model_to_dict
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.views import APIView

from core.authentication import AnonymousAuthentication
from core.response import StandardResponse
from core.stat_code import StatCode
from libs.sms.enums import SMSTemplateType
from libs.sms.utils import send_verification_code
from libs.sms.utils import verify_code
from utils.jwt_handler import jwt_encode_handler
from utils.jwt_handler import jwt_payload_handler

from .serializers.login import LoginSerializer
from .serializers.login import VerificationCodeLoginSerializer
from .serializers.sms import VerificationCodeSerializer
from .throttles import SmsRateThrottle


class VerificationCodeView(APIView):

    authentication_classes = [AnonymousAuthentication]
    throttle_classes = [SmsRateThrottle]

    def post(self, request):
        """发送短信验证码"""
        serializer = VerificationCodeSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]
        template_type = serializer.validated_data["template_type"]

        send_verification_code(
            mobile,
            template_type,
            code_length=settings.VERIFICATION_CODE_LENGTH,
            expire_time=settings.VERIFICATION_CODE_EXPIRE_TIME,
        )

        return StandardResponse(StatCode.SUCCESS)


class LoginView(APIView):
    authentication_classes = [AnonymousAuthentication]

    def post(self, request):
        """账号密码登录"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(username=username).first()

        if not user:
            raise exceptions.NotFound()

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed()

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return StandardResponse(StatCode.SUCCESS, data={"token": token})


class VerificationCodeLoginView(APIView):
    authentication_classes = [AnonymousAuthentication]

    def post(self, request):
        serializer = VerificationCodeLoginSerializer(data=request.data)

        if not serializer.is_valid():
            raise exceptions.APIException()

        mobile = serializer.validated_data["mobile"]
        code = serializer.validated_data["code"]

        # 验证验证码
        verify_code(mobile, code, SMSTemplateType.LOGIN.value)

        user, created = User.objects.get_or_create(mobile=mobile, defaults={"username": f"user_{uuid.uuid4().hex}"})

        if created:
            user.set_password(settings.DEFAULT_PASSWORD)
            user.save()

        if not user.is_active:
            return StandardResponse(StatCode.USER_IS_DISABLED, "用户被禁用")

        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save()

        # 生成token
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return StandardResponse(StatCode.SUCCESS, data={"token": token})


class AccountProfileView(APIView):
    def get(self, request):
        """获取账户信息"""
        user = request.user
        user_info = model_to_dict(user, fields=["id", "username", "mobile", "email", "avatar"])
        return StandardResponse(StatCode.SUCCESS, data=user_info)
