from typing import Optional
from fastapi.responses import JSONResponse
from app.core.exceptions import ResponseCode, StatusCode


class ResponseHandler:
    @staticmethod
    def success(
        message: Optional[str] = None,
        data: Optional[dict] = None,
        status_code: StatusCode = StatusCode.SUCCESS,
    ) -> JSONResponse:
        return JSONResponse(
            content={"message": message or "Success", "data": data},
            status_code=int(status_code.value),
        )

    @staticmethod
    def error(
        message: Optional[str] = None,
        data: Optional[dict] = None,
        code: ResponseCode = ResponseCode.BAD_REQUEST,
        status_code: StatusCode = StatusCode.ERROR,
    ) -> JSONResponse:
        return JSONResponse(
            content={"message": message or code.name, "code": code.value},
            status_code=int(status_code.value),
        )
