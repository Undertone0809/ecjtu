from fastapi import FastAPI, Depends,Header
from fastapi.security import OAuth2PasswordRequestForm

import middle
from ecjtu_schema import UserSchema, UserLoginSchema
from respose_result import ResponseResult
from auth import encode,decode

from ecjtu.client import ECJTU

app = FastAPI(title="ECJTU API", description="API for ECJTU")

app.add_middleware(middle.MyMiddleware)

@app.post("/login")
def login(user: UserLoginSchema):
    client = ECJTU(user.stud_id, user.password)
    try:
        client.login()
    except Exception as e:
        return ResponseResult.error(str(e))
    token = encode(user.stud_id, user.password)
    return ResponseResult.success({"token": token})

# gpa接口
@app.get("/gpa")
def gpa(token: str = Header(None)):
    stud_id, password = decode(token)
    client = ECJTU(stud_id, password)
    try:
        gpa = client.gpa.today()
    except Exception as e:
        return ResponseResult.error(str(e))
    return ResponseResult.success(dict(gpa))

# 启动api服务
def start_api_server():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)

if __name__ == "__main__":
    start_api_server()