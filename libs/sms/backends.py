import logging
import random
from typing import Optional
from typing import Tuple

from django.conf import settings
from django.core.cache import cache
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import models
from tencentcloud.sms.v20210111 import sms_client

from .enums import SMSTemplateType

logger = logging.getLogger(__name__)


class SMSService:
    """
    腾讯云短信服务
    相关文档：https://cloud.tencent.com/document/product/382/43196
    """

    def __init__(self, sdk_appid, secret_id, secret_key, sign_name, template_code, region):

        self.sdk_appid = sdk_appid
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.sign_name = sign_name
        self.template_code = template_code
        self.region = region

        # 初始化客户端
        _credential = credential.Credential(self.secret_id, self.secret_key)
        self.client = sms_client.SmsClient(_credential, self.region)

    def _get_verification_key(self, phone_number: str, template_type: SMSTemplateType) -> str:
        """
        获取验证码缓存键名
        :param phone_number: 手机号
        :param template_type: 模板类型
        :return: 验证码缓存键
        """
        return f"sms_{template_type}_verification_{phone_number}"

    def _get_error_count_key(self, phone_number: str, template_type: SMSTemplateType) -> str:
        """
        获取错误计数缓存键名
        :param phone_number: 手机号
        :param template_type: 模板类型
        :return: 错误计数缓存键
        """
        return f"sms_{template_type}_error_count_{phone_number}"

    def _generate_code(self, length: int = 6) -> str:
        """生成指定长度的随机数字验证码"""
        return "".join([str(random.randint(0, 9)) for _ in range(length)])

    def send_verification_code(
        self, phone_number: str, template_type: SMSTemplateType, code_length: int = 6, expire_time: int = 300
    ) -> Tuple[bool, str]:
        """
        发送验证码短信
        :param phone_number: 手机号码
        :param template_type: 验证码类型
        :param code_length: 验证码长度
        :param expire_time: 验证码过期时间(秒)
        :return: (是否成功, 消息)
        """
        # 生成随机验证码
        sms_code = self._generate_code(code_length)

        # 获取缓存键
        verification_key = self._get_verification_key(phone_number, template_type)

        try:
            # 创建发送短信请求对象
            req = models.SendSmsRequest()
            # 设置请求参数
            req.SmsSdkAppId = self.sdk_appid
            req.SignName = self.sign_name
            req.TemplateId = self.template_code
            req.TemplateParamSet = [sms_code]  # 验证码
            req.PhoneNumberSet = ["+86" + phone_number]  # 手机号格式需要加上国家码

            # 发送请求
            resp = self.client.SendSms(req)

            # 检查响应
            if resp.SendStatusSet and resp.SendStatusSet[0].Code == "Ok":
                # 发送成功，将验证码存入缓存
                cache.set(verification_key, sms_code, timeout=expire_time)

                logger.info(f"{template_type}验证码发送成功，手机号: {phone_number}")
                return True, "发送成功"
            else:
                error_msg = resp.SendStatusSet[0].Message if resp.SendStatusSet else "未知错误"
                logger.error(f"{template_type}验证码发送失败，手机号: {phone_number}, 错误: {error_msg}")
                return False, error_msg

        except TencentCloudSDKException as e:
            logger.exception(f"腾讯云短信发送异常，手机号: {phone_number}, 类型: {template_type}")
            return False, str(e)
        except Exception as e:
            logger.exception(f"短信发送异常，手机号: {phone_number}, 类型: {template_type}")
            return False, str(e)

    def verify_code(
        self,
        phone_number: str,
        code: str,
        template_type: SMSTemplateType,
        max_error_count: int = 5,
        error_count_expire: int = 300,
    ) -> Tuple[bool, str]:
        """
        验证短信验证码
        :param phone_number: 手机号码
        :param code: 用户输入的验证码
        :param template_type: 验证码类型
        :param max_error_count: 最大错误次数
        :param error_count_expire: 错误计数过期时间(秒)
        :return: (是否验证成功, 消息)
        """
        # 获取缓存键
        verification_key = self._get_verification_key(phone_number, template_type)
        error_count_key = self._get_error_count_key(phone_number, template_type)

        cached_code = cache.get(verification_key)

        if not cached_code:
            return False, "验证码已过期"

        if cached_code != code:
            # 错误次数限制
            error_count = cache.get(error_count_key, 0)

            if error_count >= max_error_count:
                cache.delete(verification_key)  # 删除验证码，需要重新获取
                cache.delete(error_count_key)  # 删除错误计数
                return False, "错误次数过多，请重新获取验证码"

            cache.set(error_count_key, error_count + 1, timeout=error_count_expire)
            return False, "验证码错误"

        # 验证成功后删除相关缓存
        # cache.delete(verification_key)
        # cache.delete(error_count_key)
        return True, "验证成功"

    def get_verification_code_ttl(self, phone_number: str, template_type: SMSTemplateType) -> Optional[int]:
        """
        获取验证码剩余有效时间
        :param phone_number: 手机号码
        :param template_type: 验证码类型
        :return: 剩余时间(秒)，如果不存在则返回None
        """
        verification_key = self._get_verification_key(phone_number, template_type)
        return cache.ttl(verification_key)


service = SMSService(
    sdk_appid=settings.TENCENT_CLOUD_SMS_SDK_APPID,
    sign_name=settings.TENCENT_CLOUD_SMS_SIGN_NAME,
    template_code=settings.TENCENT_CLOUD_SMS_TEMPLATE_CODE,
    secret_id=settings.TENCENT_CLOUD_SMS_SECRET_ID,
    secret_key=settings.TENCENT_CLOUD_SMS_SECRET_KEY,
    region=settings.TENCENT_CLOUD_SMS_REGION,
)
