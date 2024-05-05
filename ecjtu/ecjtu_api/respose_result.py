"""
构建response返回结果
{
    "code": 200,
    "msg": "success",
    "data": {
        "name": "张三",
        "age": 18
    }
}
"""
from typing import Any, Dict, Union
from fastapi.responses import JSONResponse

class ResponseResult:
    @staticmethod
    def success(data: Union[Dict[str, Any], Any] = None, msg: str = "success") -> JSONResponse:
        return JSONResponse(
            content={
                "code": 200,
                "msg": msg,
                "data": data
            }
        )
    @staticmethod
    def success_no_data(msg: str = "success") -> JSONResponse:
        return JSONResponse(
            content={
                "code": 200,
                "msg": msg,
                "data": None
            }
        )

    @staticmethod
    def not_found(data: Union[Dict[str, Any], Any] = None, msg: str = "not found") -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "msg": msg,
                "data": data
            }
        )
    
    @staticmethod
    def auth_error(data: Union[Dict[str, Any], Any] = None, msg: str = "auth error") -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "code": 401,
                "msg": msg,
                "data": data
            }
        )

    @staticmethod
    def error(data: Union[Dict[str, Any], Any] = None, msg: str = "error") -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "msg": msg,
                "data": data
            }
        )