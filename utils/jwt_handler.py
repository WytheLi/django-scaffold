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
import uuid
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import jwt
from django.conf import settings


def jwt_get_secret_key():
    """
    For enhanced security you may want to use a secret key based on user.
    """
    return settings.SECRET_KEY


def jwt_payload_handler(user):
    payload = {
        "user_id": user.pk,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRATION_DELTA),
    }
    if isinstance(user.pk, uuid.UUID):
        payload["user_id"] = str(user.pk)

    return payload


def jwt_encode_handler(payload):
    secret_key = jwt_get_secret_key()
    return jwt.encode(payload, secret_key, settings.JWT_ALGORITHM)


def jwt_decode_handler(token):
    options = {
        "verify_exp": settings.JWT_VERIFY_EXPIRATION,
    }
    secret_key = jwt_get_secret_key()
    return jwt.decode(
        token, secret_key, options=options, leeway=settings.JWT_LEEWAY, algorithms=[settings.JWT_ALGORITHM]
    )


def jwt_get_user_id_from_payload_handler(payload):
    return payload.get("user_id")
