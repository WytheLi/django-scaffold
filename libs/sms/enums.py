from enum import Enum


class SMSTemplateType(Enum):
    """短信模板类型枚举"""

    REGISTER = "register"  # 注册验证码
    LOGIN = "login"  # 登录验证码
    RESET_PASSWORD = "reset_password"  # 重置密码验证码
    BIND_PHONE = "bind_phone"  # 绑定手机验证码
    CHANGE_PHONE = "change_phone"  # 更换手机验证码
