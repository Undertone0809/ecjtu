from starlette.middleware.base import BaseHTTPMiddleware

from ecjtu.server import auth, respose_result


class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # not secure routes
        secure_routes = [
            "/refresh_token",
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
            # if not header, return response
            if not header:
                return response
            # get stud_id from access_token
            try:
                stud_id = auth.get_stud_id(header)
            except Exception as e:
                return respose_result.ResponseResult.auth_error(str(e))
            if not stud_id:
                response = respose_result.ResponseResult.auth_error(
                    "access_token令牌已过期，请刷新"
                )
                return response
        response = await call_next(request)

        return response
