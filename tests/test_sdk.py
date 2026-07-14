import asyncio

from ecjtu import ECJTU, ScheduledCourse
from ecjtu.crud import (
    GPACRUD,
    AsyncScheduledCourseCRUD,
    ElectiveCourseCRUD,
    ScheduledCourseCRUD,
    ScoreCRUD,
)
from ecjtu.server.api import app
from ecjtu.server.auth import decode_data, encode_data

COURSE_PAYLOAD = {
    "classSpan": "1,2",
    "course": "高等数学",
    "className": "高等数学(20261-1)",
    "weekSpan": "1-16",
    "courseRequire": "必修课",
    "teacherName": "张老师",
    "weekDay": 1,
    "classRoom": "31-101",
    "pkType": "上课",
}


class StubResponse:
    def __init__(self, *, json_data=None, text="", status_code=200):
        self._json_data = json_data or {}
        self.text = text
        self.status_code = status_code

    def json(self):
        return self._json_data


class StubClient:
    def __init__(self, response):
        self.response = response

    def get(self, *args, **kwargs):
        return self.response

    def post(self, *args, **kwargs):
        return self.response


class AsyncStubClient:
    def __init__(self, response):
        self.response = response

    async def get(self, *args, **kwargs):
        return self.response

    async def post(self, *args, **kwargs):
        return self.response


def test_package_client_initializes_with_existing_cookie():
    with ECJTU(cookie={"CASTGC": "test-cookie"}) as client:
        assert client.has_login is True


def test_scheduled_course_model_accepts_upstream_aliases():
    course = ScheduledCourse.model_validate(COURSE_PAYLOAD)

    assert course.course_name == "高等数学(20261-1)"
    assert course.model_dump(by_alias=True)["classRoom"] == "31-101"


def test_scheduled_course_crud_parses_response():
    response = StubResponse(json_data={"weekcalendarpojoList": [COURSE_PAYLOAD]})
    courses = ScheduledCourseCRUD(StubClient(response)).filter(date="2026-07-15")

    assert len(courses) == 1
    assert courses[0].teacher == "张老师"


def test_async_scheduled_course_crud_parses_response():
    response = StubResponse(json_data={"weekcalendarpojoList": [COURSE_PAYLOAD]})
    crud = AsyncScheduledCourseCRUD(AsyncStubClient(response))

    courses = asyncio.run(crud.filter(date="2026-07-15"))

    assert len(courses) == 1
    assert courses[0].course == "高等数学"


def test_gpa_crud_parses_html():
    html = """
    <table>
      <tr></tr><tr></tr><tr></tr>
      <tr>
        <td>0</td><td>Zeeland</td><td>正常</td><td>3</td>
        <td>4</td><td>5</td><td>3.92</td>
      </tr>
    </table>
    """
    gpa = GPACRUD(StubClient(StubResponse(text=html))).today()

    assert gpa.student_name == "Zeeland"
    assert gpa.gpa == "3.92"


def test_score_crud_parses_html():
    html = """
    <ul class="2026_1">
      <li>0</li><li>高等数学</li><li>必修课</li>
      <li>3</li><li>4.0</li><li>95</li>
    </ul>
    """
    scores = ScoreCRUD(StubClient(StubResponse(text=html))).filter(semester="2026.1")

    assert len(scores) == 1
    assert scores[0].credit == 4.0
    assert scores[0].grade == "95"


def test_elective_course_crud_parses_html():
    cells = [
        "2026.1",
        "1",
        "2",
        "3",
        "必修课",
        "考试",
        "6",
        "3.0",
        "星期一 第1,2节",
        "张老师",
        "10",
        "高等数学教学班",
        "A01",
    ]
    html = "<table><tbody><tr>{}</tr></tbody></table>".format(
        "".join(f"<td>{cell}</td>" for cell in cells)
    )
    courses = ElectiveCourseCRUD(StubClient(StubResponse(text=html))).filter(
        semester="2026.1"
    )

    assert len(courses) == 1
    assert courses[0].class_number == "A01"
    assert courses[0].teacher == "张老师"


def test_server_routes_are_registered():
    paths = {route.path for route in app.routes}

    assert "/login" in paths
    assert "/schedule/{date}" in paths
    assert "/elective_courses/{semester}" in paths


def test_auth_encoding_round_trip():
    value = "20260001:access_token:2026-07-15T00:00:00+00:00"

    assert decode_data(encode_data(value)) == value
