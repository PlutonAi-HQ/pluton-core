# app/core/exceptions.py
from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(str, Enum):
    DUPLICATE_EMAIL = "DUPLICATE_EMAIL"
    DUPLICATE_USERNAME = "DUPLICATE_USERNAME"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppException(Exception):
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        status_code: int = 400,
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}
        super().__init__(message)
