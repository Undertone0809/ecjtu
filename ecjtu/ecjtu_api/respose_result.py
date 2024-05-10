from typing import Any

from fastapi.responses import JSONResponse


class ResponseResult:
    @staticmethod
    def success(data: Any = None, msg: str = "success") -> JSONResponse:
        return JSONResponse(content={"code": 200, "msg": msg, "data": data})

    @staticmethod
    def success_no_data(msg: str = "success") -> JSONResponse:
        return JSONResponse(content={"code": 200, "msg": msg, "data": None})

    @staticmethod
    def not_found(data: str = None, msg: str = "not found") -> JSONResponse:
        return JSONResponse(
            status_code=404, content={"code": 404, "msg": msg, "data": data}
        )

    @staticmethod
    def auth_error(data: str = None, msg: str = "auth error") -> JSONResponse:
        return JSONResponse(
            status_code=401, content={"code": 401, "msg": msg, "data": data}
        )

    @staticmethod
    def param_error(data: str = None, msg: str = "param error") -> JSONResponse:
        return JSONResponse(
            status_code=400, content={"code": 400, "msg": msg, "data": data}
        )

    @staticmethod
    def error(data: str = None, msg: str = "error") -> JSONResponse:
        return JSONResponse(
            status_code=500, content={"code": 500, "msg": msg, "data": data}
        )
