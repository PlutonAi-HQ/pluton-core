# app/core/exceptions.py
from enum import Enum
from typing import Optional, Dict, Any


class ResponseCode(Enum):
    SUCCESS = 1000
    DUPLICATE_ENTRY = 1001
    DUPLICATE_EMAIL = 1002
    DUPLICATE_USERNAME = 1003
    INVALID_CREDENTIALS = 1004
    NOT_FOUND = 1005
    UNAUTHORIZED = 1006
    FORBIDDEN = 1007
    VALIDATION_ERROR = 1008
    DATABASE_ERROR = 1009
    INTERNAL_ERROR = 1010
    USER_NOT_FOUND = 1011
    REFERRAL_NOT_FOUND = 1012
    REFERRAL_ALREADY_USED = 1013
    REFERRAL_NOT_OWNER = 1014
    REFERRAL_ALREADY_EXISTS = 1015
    CONVERSATION_NOT_FOUND = 1016
    SESSION_NOT_FOUND = 1017
    BAD_REQUEST = 1018


class StatusCode(str, Enum):
    OK = "200"
    CREATED = "201"
    NO_CONTENT = "204"
    BAD_REQUEST = "400"
    UNAUTHORIZED = "401"
    FORBIDDEN = "403"
    NOT_FOUND = "404"
    INTERNAL_SERVER_ERROR = "500"


class AppException(Exception):
    def __init__(
        self,
        error_code: ResponseCode,
        message: str,
        status_code: int = 400,
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}
        super().__init__(message)
