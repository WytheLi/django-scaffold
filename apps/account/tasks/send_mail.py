import logging

from account.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from core.celery import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """
    发送欢迎邮件任务
    """
    try:
        user = User.objects.get(id=user_id)

        # 准备邮件内容
        subject = "欢迎加入我们的平台"
        html_content = render_to_string("email/welcome.html", {"user": user, "site_name": "Django Scaffold"})
        text_content = strip_tags(html_content)

        # 创建邮件
        email = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")

        # 发送邮件
        email.send()

        logger.info(f"欢迎邮件已发送至 {user.email}")
        return f"欢迎邮件已发送至 {user.email}"

    except Exception as exc:
        logger.error(f"发送欢迎邮件失败: {exc}")
        # 重试任务（最多3次）
        self.retry(exc=exc, countdown=60)
