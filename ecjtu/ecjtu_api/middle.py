from starlette.middleware.base import BaseHTTPMiddleware

from . import auth, respose_result


class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 不被拦截的路由
        secure_routes = [
            "/token",
            "/login",
            "/",
            "/docs",
            "/docs/",
            "/openapi.json",
            "/favicon.ico",
        ]

        response = respose_result.ResponseResult.auth_error()
        path = request.url.path

        if path not in secure_routes:
            header = request.headers.get("token")
            # 是否存在token
            if not header:
                return response
            token = header
            stud_id, enc_pwd = auth.decode(token)
            if not stud_id or not enc_pwd:
                return response
        response = await call_next(request)

        return response
