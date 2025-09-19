import logging

from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from core.response import StandardResponse

logger = logging.getLogger(__name__)


class AppExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        """
            App后台错误统一处理，标准化响应
        :param request:
        :param exception:
        :return:
        """
        # 记录异常信息
        logger.error(f"Exception occurred: {str(exception)}", exc_info=True)

        return StandardResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR, msg=_("Internal Server Error"), data={"error": str(exception)}
        )
