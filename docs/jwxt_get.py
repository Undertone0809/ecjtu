import json
import re

import requests
from bs4 import BeautifulSoup


def get_enc_password(origin_pwd: str) -> str:
    ENC_URL = "http://cas.ecjtu.edu.cn/cas/loginPasswdEnc"
    enc_response = requests.post(ENC_URL, data={"pwd": origin_pwd})

    _ = enc_response.content.decode("utf8").replace("'", '"')
    return json.loads(_)["passwordEnc"]


ecjtu_login = "http://cas.ecjtu.edu.cn/cas/login"  # 智慧交大登录页
jwxt_login = "https://jwxt.ecjtu.edu.cn/stuMag/Login_dcpLogin.action"  # 教务系统登录页
ecjtu_to_jwxt = "http://cas.ecjtu.edu.cn/cas/login?service=https%3A%2F%2Fjwxt.ecjtu.edu.cn%2FstuMag%2FLogin_dcpLogin.action"  # 智慧交大登录教务系统
get_classes = "https://jwxt.ecjtu.edu.cn/Schedule/Weekcalendar_getTodayWeekcalendar.action"  # 获取课程信息(post)
get_grade = "https://jwxt.ecjtu.edu.cn/scoreQuery/stuScoreQue_getStuScore.action?item=0401"  # 获取成绩信息(get)


def login(username: str, password: str, session: requests.Session) -> requests.Session:
    # 关闭警告
    requests.packages.urllib3.disable_warnings()
    # 获取密码
    enc = get_enc_password(password)
    # 打包登录body
    login_data = {
        "username": username,
        "password": enc,
        "lt": "",
        "service": "http://portal.ecjtu.edu.cn/dcp/index.jsp",
    }
    # 获取lt
    headers = {
        # 设置UA
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        # 设置Host
        "Host": "cas.ecjtu.edu.cn",
    }
    response = session.get(ecjtu_login, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    login_data["lt"] = soup.find("input", {"name": "lt"})["value"]
    # 登录
    headers_append = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "http://cas.ecjtu.edu.cn/cas/login",
    }
    headers.update(headers_append)
    response = session.post(
        ecjtu_login, data=login_data, headers=headers, allow_redirects=False
    )
    if not response.cookies.get("CASTGC"):
        print("账户或密码错误")
        return None
    # 获取教务JSESSIONID
    session.get(jwxt_login, headers=headers, allow_redirects=False, verify=False)
    # 获取教务跳转登录链接
    response_url = session.get(ecjtu_to_jwxt, allow_redirects=False)
    # 登录教务系统
    result = session.get(response_url.headers["Location"])
    if result.status_code != 200:
        print("教务系统错误，登录失败")
        return None
    print("登录成功")
    return session


session = requests.Session()
login("2022211003000111", "mzdwzyddn0", session)
grade_html = session.get(get_grade)


def get_grade_count(grade_html: requests.Response) -> dict:
    soup = BeautifulSoup(grade_html.text, "html.parser")
    data_row = soup.find_all("tr")[3]
    data = [td.text for td in data_row.find_all("td")]
    grade_count = {
        "姓名": data[1],
        "班级": data[2],
        "平均学分绩点": data[6],
    }
    return grade_count


print(get_grade_count(grade_html))


def get_grade_from_semester(semester: str, grade_html: requests.Response) -> list:
    tsemester = semester.replace(".", "_")
    grade_from_semester_list = []
    soup = BeautifulSoup(grade_html.text, "html.parser")

    pattern = re.compile(r"\b{}\b".format(tsemester))
    ul_tags = soup.find_all("ul", class_=pattern)
    for ul_tag in ul_tags:
        li_list = ul_tag.find_all("li")
        li_values = [li.text for li in li_list]
        grade_from_semester = {
            "课程学期": semester,
            "课程": {
                "课程名": li_values[1],
                "课程性质": li_values[2],
                "学分": li_values[4],
                "成绩": li_values[5],
            },
        }
        grade_from_semester_list.append(grade_from_semester)
    return grade_from_semester_list


print(get_grade_from_semester("2022.1", grade_html))
