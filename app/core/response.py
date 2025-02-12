from typing import Optional
from fastapi.responses import JSONResponse


class ResponseHandler:
    @staticmethod
    def success(message: str, data: Optional[dict] = None) -> JSONResponse:
        return JSONResponse(content={"message": message, "data": data}, status_code=200)

    @staticmethod
    def error(
        message: str, data: Optional[dict] = None, code: int = 400
    ) -> JSONResponse:
        return JSONResponse(
            content={"message": message, "data": data, "code": code}, status_code=400
        )
