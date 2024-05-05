from starlette.middleware.base import BaseHTTPMiddleware
from respose_result import ResponseResult
from auth import decode

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 不被拦截的路由
        secure_routes = ["/token","/login","/","/docs","/openapi.json","/favicon.ico"]

        response = ResponseResult.auth_error()
        path = request.url.path

        if path not in secure_routes:
            header = request.headers.get("token")
            # 是否存在token
            if not header:
                return response
            token = header
            stud_id, enc_pwd = decode(token)
            if not stud_id or not enc_pwd:
                return response
        response = await call_next(request)

        return response



        