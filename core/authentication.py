#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本模块实现了JWT生成签名、签名验证功能

此部分代码参考了 [djangorestframework-jwt]，其原始项目地址为：
https://github.com/jpadilla/django-rest-framework-jwt

原项目遵循 [MIT] 许可证。
本代码在参考时已遵循相关许可证要求。

===========================================================
This module implements the functions of generating signatures and verifying signatures for JWT.

This code is inspired by/or adapted from [djangorestframework-jwt],
original project can be found at:
https://github.com/jpadilla/django-rest-framework-jwt

The original project is licensed under the [MIT] license.
This adaptation follows the terms of that license.
"""
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import get_authorization_header

from utils.jwt_handler import jwt_decode_handler
from utils.jwt_handler import jwt_get_user_id_from_payload_handler


class JWTTokenAuthentication(TokenAuthentication):
    keyword = settings.JWT_AUTH_HEADER_PREFIX

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            # 没有Authorization头，返回None，让其他认证类处理
            return None

        if smart_str(auth[0].lower()) != auth_header_prefix:
            # 有Authorization头，但前缀不匹配，返回None，让其他认证类处理
            return None

        if len(auth) == 1:
            msg = _("Invalid Authorization header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid Authorization header. Credentials string " "should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        user_id = jwt_get_user_id_from_payload_handler(payload)

        if not user_id:
            msg = _("Invalid payload.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            # 自动处理异常。找不到会抛 User.DoesNotExist，找到多个会抛 User.MultipleObjectsReturned
            # user = User.objects.get_by_natural_key(username)
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            msg = _("Invalid signature.")
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _("User account is disabled.")
            raise exceptions.AuthenticationFailed(msg)

        return user

    def authenticate(self, request):
        """
        Clients should authenticate by passing the token key in the "Authorization"
        HTTP header, prepended with the string specified in the setting
        `JWT_AUTH_HEADER_PREFIX`. For example:

            Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
        """
        jwt_value = self.get_jwt_value(request)

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignatureError:
            return False

        user = self.authenticate_credentials(payload)

        return (user, jwt_value)
