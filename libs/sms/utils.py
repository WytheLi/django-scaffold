from .backends import service
from .enums import SMSTemplateType
from .exceptions import SMSSendException
from .exceptions import SMSVerificationException


def send_verification_code(phone_number: str, template_type: SMSTemplateType, **kwargs):
    """
    发送验证码的快捷函数
    :param phone_number: 手机号码
    :param template_type: 验证码类型
    :return: None
    :raises: SMSSendException 当发送失败时抛出
    """
    success, message = service.send_verification_code(phone_number, template_type, **kwargs)

    if not success:
        raise SMSSendException(message)


def verify_code(phone_number: str, code: str, template_type: SMSTemplateType, **kwargs):
    """
    验证验证码的快捷函数
    :param phone_number: 手机号码
    :param code: 验证码
    :param template_type: 验证码类型
    :return: None
    :raises: SMSVerificationException 当验证失败时抛出
    """
    success, message = service.verify_code(phone_number, code, template_type, **kwargs)

    if not success:
        raise SMSVerificationException(message)
