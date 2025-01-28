from typing import Optional


class ResponseHandler:
    def success(self, message: str, data: Optional[dict] = None) -> dict:
        return {"message": message, "data": data}

    def error(self, message: str, data: Optional[dict] = None, code: int = 400) -> dict:
        return {"message": message, "data": data, "code": code}
