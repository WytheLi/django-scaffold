from typing import Any

from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _


class StandardResponse(JsonResponse):
    """
    Standard Response format.
    """

    def __init__(self, code: int, msg: str = _("success"), data: Any = None, **kwargs):
        content = {"code": code, "message": msg}

        if data is not None:
            content.update({"data": data})

        super().__init__(data=content, **kwargs)
