import datetime
import re

from fastapi import FastAPI, Header
from fastapi.responses import RedirectResponse

from ecjtu.client import ECJTU

from . import auth, middle, respose_result, schema

app = FastAPI(title="ECJTU API", description="API for ECJTU")

app.add_middleware(middle.MyMiddleware)


@app.get("/", include_in_schema=False)
def push_docs():
    respose = RedirectResponse(url="/docs")
    return respose


@app.post(
    "/login",
    tags=["登录"],
    summary="登录",
    description="登录并获取token,以下所有接口都需要token才可以使用",
)
def login(user: schema.UserLoginSchema):
    try:
        access_token, refresh_token = auth.create_tokens(user.stud_id, user.password)
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))

    return respose_result.ResponseResult.success(
        {"access_token": access_token, "refresh_token": refresh_token}
    )


@app.post(
    "/refresh_token",
    tags=["登录"],
    summary="刷新access_token",
    description="刷新access_token",
)
def refresh_token(data: str = None):
    try:
        access_token = auth.refresh_access_token(data)
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    return respose_result.ResponseResult.success({"access_token": access_token})


# gpa接口
@app.get("/gpa", tags=["GPA"], summary="获取GPA", description="获取当学期GPA")
def gpa(token: str = Header(None)):
    stud_id = auth.get_stud_id(token)
    cookie = auth.get_cookie(stud_id)
    client = ECJTU(cookie=cookie)
    try:
        gpa = client.gpa.today()
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    return respose_result.ResponseResult.success(dict(gpa))


# 课表接口
@app.get("/schedule", tags=["课表"], summary="获取当天课表", description="获取当天课表")
def schedule(token: str = Header(None)):
    stud_id = auth.get_stud_id(token)
    cookie = auth.get_cookie(stud_id)
    client = ECJTU(cookie=cookie)
    try:
        schedule = client.scheduled_courses.today()
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    schedule_list = []
    for sublist in schedule:
        schedule_list.append(dict(sublist))
    return respose_result.ResponseResult.success(schedule_list)


@app.get(
    "/schedule/{date}",
    tags=["课表"],
    summary="获取指定日期课表",
    description="获取指定日期课表,指定日期格式为yyyy-mm-dd",
)
def schedule_date(token: str = Header(None), date: str = None):
    # date(str): The date to filter, eg: 2023-01-01
    try:
        valid_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return respose_result.ResponseResult.param_error("日期格式错误")

    stud_id = auth.get_stud_id(token)
    cookie = auth.get_cookie(stud_id)
    client = ECJTU(cookie=cookie)
    try:
        scheduled_courses = client.scheduled_courses.filter(date=valid_date)
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    schedule_list = []
    for sublist in scheduled_courses:
        schedule_list.append(dict(sublist))
    return respose_result.ResponseResult.success(schedule_list)


@app.get(
    "/schedule_week", tags=["课表"], summary="获取本周课表", description="获取本周课表"
)
def schedule_week(token: str = Header(None)):
    stud_id = auth.get_stud_id(token)
    cookie = auth.get_cookie(stud_id)
    client = ECJTU(cookie=cookie)
    try:
        schedule = client.scheduled_courses.this_week()
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    dict_list = []
    for sublist in schedule:
        dict_sublist = []
        for item in sublist:
            dict_sublist.append(dict(item))
        dict_list.append(dict_sublist)
    return respose_result.ResponseResult.success(dict_list)


# 成绩接口
@app.get("/score", tags=["成绩"], summary="获取当前成绩", description="获取当学期成绩")
def score(token: str = Header(None)):
    stud_id = auth.get_stud_id(token)
    cookie = auth.get_cookie(stud_id)
    client = ECJTU(cookie=cookie)
    try:
        score = client.scores.today()
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    score_list = []
    for sublist in score:
        score_list.append(dict(sublist))
    return respose_result.ResponseResult.success(score_list)


@app.get(
    "/score/{semester}",
    tags=["成绩"],
    summary="获取指定学期成绩",
    description="获取指定学期成绩,semester格式为yyyy.1或yyyy.2",
)
def score_semester(token: str = Header(None), semester: str = None):
    # semester(Optional[str]): The semester to filter, eg: 2023.1, 2023.2
    if not re.match(r"\d{4}\.[12]", semester):
        return respose_result.ResponseResult.param_error("学期格式错误")
    stud_id = auth.get_stud_id(token)
    cookie = auth.get_cookie(stud_id)
    client = ECJTU(cookie=cookie)
    try:
        scores = client.scores.filter(semester=semester)
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    score_list = []
    for sublist in scores:
        score_list.append(dict(sublist))
    return respose_result.ResponseResult.success(score_list)


# 选课情况接口
@app.get(
    "/elective_courses",
    tags=["选课情况"],
    summary="获取当前选课情况",
    description="获取当前学期选课情况",
)
def elective_courses(token: str = Header(None)):
    stud_id = auth.get_stud_id(token)
    cookie = auth.get_cookie(stud_id)
    client = ECJTU(cookie=cookie)
    try:
        elective_courses = client.elective_courses.today()
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    elective_courses_list = []
    for sublist in elective_courses:
        elective_courses_list.append(dict(sublist))
    return respose_result.ResponseResult.success(elective_courses_list)


@app.get(
    "/elective_courses/{semester}",
    tags=["选课情况"],
    summary="获取指定学期选课情况",
    description="获取指定学期选课情况,semester格式为yyyy.1或yyyy.2",
)
def elective_courses_semester(token: str = Header(None), semester: str = None):
    # semester(Optional[str]): The semester to filter, eg: 2023.1, 2023.2
    if not re.match(r"\d{4}\.[12]", semester):
        return respose_result.ResponseResult.param_error("学期格式错误")
    stud_id = auth.get_stud_id(token)
    cookie = auth.get_cookie(stud_id)
    client = ECJTU(cookie=cookie)
    try:
        elective_courses = client.elective_courses.filter(semester=semester)
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    elective_courses_list = []
    for sublist in elective_courses:
        elective_courses_list.append(dict(sublist))
    return respose_result.ResponseResult.success(elective_courses_list)


# 启动api服务
def start_api_server(port=8080):
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=port)
