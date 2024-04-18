import json
import re
import os
import httpx
from bs4 import BeautifulSoup


def get_enc_password(origin_pwd: str) -> str:
    ENC_URL = "http://cas.ecjtu.edu.cn/cas/loginPasswdEnc"
    enc_response = httpx.post(ENC_URL, data={"pwd": origin_pwd})

    _ = enc_response.content.decode("utf8").replace("'", '"')
    return json.loads(_)["passwordEnc"]

ecjtu_login = "http://cas.ecjtu.edu.cn/cas/login"  # 智慧交大登录页
jwxt_login = "https://jwxt.ecjtu.edu.cn/stuMag/Login_dcpLogin.action"  # 教务系统登录页
ecjtu_to_jwxt = "http://cas.ecjtu.edu.cn/cas/login?service=https%3A%2F%2Fjwxt.ecjtu.edu.cn%2FstuMag%2FLogin_dcpLogin.action"  # 智慧交大登录教务系统
get_classes = "https://jwxt.ecjtu.edu.cn/Schedule/Weekcalendar_getTodayWeekcalendar.action"  # 获取课程信息(post)
get_grade = "https://jwxt.ecjtu.edu.cn/scoreQuery/stuScoreQue_getStuScore.action?item=0401"  # 获取成绩信息(get)
get_elective_course = "https://jwxt.ecjtu.edu.cn/infoQuery/XKStu_findTerm.action?term=2023.2"  # 获取选修课程信息(get)

def create_session(username: str,password: str,session: httpx.Client) -> httpx.Client:
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
    # print(response.content)
    soup = BeautifulSoup(response.content, "html.parser")
    login_data["lt"] = soup.find("input", {"name": "lt"})["value"]
    # 登录
    headers_append = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "http://cas.ecjtu.edu.cn/cas/login",
    }
    headers.update(headers_append)
    response = session.post(
        ecjtu_login, data=login_data, headers=headers
    )
    print(response.cookies)
    response = session.get(jwxt_login, headers=headers)
    response_url = session.get(ecjtu_to_jwxt)
    result = session.get(response_url.headers['Location'],follow_redirects=True)
    if result.status_code != 200:
        print("教务系统错误，登录失败")
        return None
    print("登录成功")
    return session

def get_ele_course(session: httpx.Client):
    classes = session.post(get_elective_course)
    soup = BeautifulSoup(classes.text, "html.parser")
    tbody_tag = soup.find("tbody")
    tr_list = tbody_tag.find_all("tr")
    for tr_tag in tr_list:
        td_tags = tr_tag.find_all("td")
        td = [td.text for td in td_tags]
        print(td)
        ele_course = {
            # "semester": semester,
            "class_name": td[11],
            "class_type": td[4],
            "class_assessment_method": td[5],
            "class_info": td[8],
            "class_number": td[12],
            "credit": float(td[7]),
            "teacher": td[9]
        }
        print(ele_course)
    # tr_list = tr_pattern.findall(tbody_tag)
    # for tr_tag in tr_list:
        # print(tr_tag)
    # print(tr_list)

def main():
    client = httpx.Client(verify=False)
    # enc = get_enc_password("20030115b")
    # print(enc)
    session = create_session("2022211003000112","20030115b",client)
    get_ele_course(session)
    # print(session.cookies)
    # print(classes.text)

if __name__ == "__main__":
    main()



# async def create_session(username: str, password: str,session: httpx.AsyncClient) -> httpx.AsyncClient:
#         # 获取密码
#         enc = get_enc_password(password)
#         # 打包登录body
#         login_data = {
#             "username": username,
#             "password": enc,
#             "lt": "",
#             "service": "http://portal.ecjtu.edu.cn/dcp/index.jsp",
#         }
#         # 获取lt
#         headers = {
#             # 设置UA
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
#             # 设置Host
#             "Host": "cas.ecjtu.edu.cn",
#         }
#         response =await session.get(ecjtu_login, headers=headers)
#         # print(response.content)
#         soup = BeautifulSoup(response.content, "html.parser")
#         login_data["lt"] = soup.find("input", {"name": "lt"})["value"]
#         # 登录
#         headers_append = {
#             "Content-Type": "application/x-www-form-urlencoded",
#             "Referer": "http://cas.ecjtu.edu.cn/cas/login",
#         }
#         headers.update(headers_append)
#         response =await session.post(
#             ecjtu_login, data=login_data, headers=headers
#         )
#         print(response.cookies)
#         response = await session.get(jwxt_login, headers=headers)
#         response_url =await session.get(ecjtu_to_jwxt)
#         result =await session.get(response_url.headers['Location'],follow_redirects=True)
#         if result.status_code != 200:
#             print("教务系统错误，登录失败")
#             return None
#         print("登录成功")
#         return session


# async def main():
#     client = httpx.AsyncClient(verify=False)
#     session = await create_session("2022211003000111", "mzdwzyddn0",client)
#     classes = await session.post(get_classes,data={"date":"2024-04-05"})
#     for k,v in classes.json().items():
#         if k == "weekcalendarpojoList":
#             for item in v:
#                 for i,j in item.items():
#                     print(i," ",j)
#                 print("\n")


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
