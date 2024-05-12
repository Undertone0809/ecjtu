import datetime
import re

from fastapi import FastAPI, Header
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse

from ecjtu.client import ECJTU
from ecjtu.server import auth, middle, respose_result, schema

app = FastAPI(title="ECJTU API", description="API for ECJTU")

app.add_middleware(middle.MyMiddleware)


@app.get("/", include_in_schema=False)
def push_docs():
    response = RedirectResponse(url="/docs")
    return response


@app.post(
    "/login",
    tags=["登录"],
    summary="登录",
    description="登录获取access_token和refresh_token,access_token用于之后的所有请求,refresh_token用于刷新access_token",
    # noqa
)
def login(user: schema.UserLoginSchema) -> JSONResponse:
    """login

    Args:
        user (schema.UserLoginSchema): user login info

    Returns:
        JSONResponse: response
    """
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
    """refresh access token

    Args:
        data(str): refresh token

    Returns:
        JSONResponse: access token

    """
    try:
        access_token = auth.refresh_access_token(data)
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    return respose_result.ResponseResult.success({"access_token": access_token})


def create_client(token: str) -> ECJTU:
    """create client

    Args:
        token (str): access token

    Returns:
        ECJTU: client
    """
    stud_id = auth.get_stud_id(token)
    cookie = auth.get_cookie(stud_id)
    client = ECJTU(cookie=cookie)
    return client


@app.get("/gpa", tags=["GPA"], summary="获取GPA", description="获取当学期GPA")
def gpa(token: str = Header(None)):
    """get gpa

    Args:
        token: access token

    Returns:
        JSONResponse: gpa

    """
    client = create_client(token)
    try:
        gpa = client.gpa.today()
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    return respose_result.ResponseResult.success(dict(gpa))


@app.get("/schedule", tags=["课表"], summary="获取当天课表", description="获取当天课表")
def schedule(token: str = Header(None)):
    """get schedule of today

    Args:
        token: access token

    Returns:
        JSONResponse: schedule of today

    """
    client = create_client(token)
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
    """get schedule of specified date

    Args:
        token: access token
        date: date in format yyyy-mm-dd

    Returns:
        JSONResponse: schedule of specified date

    """
    try:
        valid_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return respose_result.ResponseResult.param_error("日期格式错误")
    client = create_client(token)
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
    """get schedule of this week

    Args:
        token: access token

    Returns:
        JSONResponse: schedule of this week

    """
    client = create_client(token)
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


@app.get("/score", tags=["成绩"], summary="获取当前成绩", description="获取当学期成绩")
def score(token: str = Header(None)):
    """get score of this semester

    Args:
        token: access token

    Returns:
        JSONResponse: score of this semester

    """
    client = create_client(token)
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
    """get score of specified semester

    Args:
        token: access token
        semester: semester in format yyyy.1 or yyyy.2

    Returns:
        JSONResponse: score of specified semester

    """
    if not re.match(r"\d{4}\.[12]", semester):
        return respose_result.ResponseResult.param_error("学期格式错误")
    client = create_client(token)
    try:
        scores = client.scores.filter(semester=semester)
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    score_list = []
    for sublist in scores:
        score_list.append(dict(sublist))
    return respose_result.ResponseResult.success(score_list)


@app.get(
    "/elective_courses",
    tags=["选课情况"],
    summary="获取当前选课情况",
    description="获取当前学期选课情况",
)
def elective_courses(token: str = Header(None)):
    """get elective courses

    Args:
        token: access token

    Returns:
        JSONResponse: elective courses

    """
    client = create_client(token)
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
    """get elective courses of specified semester

    Args:
        token: access token
        semester: semester in format yyyy.1 or yyyy.2

    Returns:
        JSONResponse: elective courses
    """
    if not re.match(r"\d{4}\.[12]", semester):
        return respose_result.ResponseResult.param_error("学期格式错误")
    client = create_client(token)
    try:
        elective_courses = client.elective_courses.filter(semester=semester)
    except Exception as e:
        return respose_result.ResponseResult.error(str(e))
    elective_courses_list = []
    for sublist in elective_courses:
        elective_courses_list.append(dict(sublist))
    return respose_result.ResponseResult.success(elective_courses_list)


def start_api_server(port: int = 8080) -> None:
    """start api server

    Args:
        port (int, optional): port to run the server on. Defaults to 8080.

    Raises:
        Exception: if port is already in use, an exception will be raised.
    """
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=port)
