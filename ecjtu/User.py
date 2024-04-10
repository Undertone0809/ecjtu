import requests
from bs4 import BeautifulSoup
import os
import json
import re
import webbrowser
import datetime
import pandas as pd

class User:
    # 相关URL
    ecjtu_login = "http://cas.ecjtu.edu.cn/cas/login" # 智慧交大登录页
    jwxt_login = "https://jwxt.ecjtu.edu.cn/stuMag/Login_dcpLogin.action" # 教务系统登录页
    ecjtu_to_jwxt = "http://cas.ecjtu.edu.cn/cas/login?service=https%3A%2F%2Fjwxt.ecjtu.edu.cn%2FstuMag%2FLogin_dcpLogin.action" #智慧交大登录教务系统
    Get_classes = "https://jwxt.ecjtu.edu.cn/Schedule/Weekcalendar_getTodayWeekcalendar.action" # 获取课程信息(post)
    Get_grade = "https://jwxt.ecjtu.edu.cn/scoreQuery/stuScoreQue_getStuScore.action?item=0401" # 获取成绩信息(get)

    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session = User.login(username,password,self.session)
        if self.session == None:
            raise Exception("登录失败")
    
    @staticmethod
    def get_enc_password(origin_pwd: str) -> str:
        """获取加密后的密码"""
        ENC_URL = 'http://cas.ecjtu.edu.cn/cas/loginPasswdEnc'
        enc_response = requests.post(ENC_URL, data={'pwd': origin_pwd})

        _ = enc_response.content.decode('utf8').replace("'", '"')
        return json.loads(_)['passwordEnc']
    @staticmethod
    def login(username:str,password:str,session:requests.Session) -> requests.Session:
        """登录教务系统"""
        # 关闭警告
        requests.packages.urllib3.disable_warnings()
        # 获取密码
        enc = User.get_enc_password(password)
        # 打包登录body
        login_data = {
            'username': username,
            'password': enc,
            'lt': '',
            "service":"http://portal.ecjtu.edu.cn/dcp/index.jsp",
        }
        # 获取lt
        headers = {
            # 设置UA
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            # 设置Host
            "Host": "cas.ecjtu.edu.cn"
        }
        response = session.get(User.ecjtu_login,headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        login_data['lt'] = soup.find('input', {'name': 'lt'})['value']
        # 登录
        headers_append = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://cas.ecjtu.edu.cn/cas/login"
          }
        headers.update(headers_append)
        response = session.post(User.ecjtu_login, data=login_data,headers=headers,allow_redirects=False)
        if not response.cookies.get('CASTGC'):
            print("账户或密码错误")
            return None
        # 获取教务JSESSIONID
        session.get(User.jwxt_login,headers=headers,allow_redirects=False,verify=False)
        # 获取教务跳转登录链接
        response_url = session.get(User.ecjtu_to_jwxt,allow_redirects=False)
        # 登录教务系统
        result = session.get(response_url.headers['Location'])
        if result.status_code != 200:
            print("教务系统错误，登录失败")
            return None
        print("登录成功")
        return session
    
    def get_classes_tofile(self,date:str = datetime.datetime.now().strftime("%Y-%m-%d")) -> str:
        """读取指定的课程情况，否则读取今天的课程
           保存到本目录下的excel文件和html文件,并打开excel文件"""
        classes = self.session.post(self.Get_classes,data={"date":date})
        # for k,v in classes.json().items():
        #     if k == "weekcalendarpojoList":
        #         if len(v) == 0:
        #             print("今天没有课哦")
        #             return None
        #         for item in v:
        #             for i,j in item.items():
        #                 print(i," ",j)
        #             print("\n")
        # return None
        #处理json数据
        #返回今天的课（课程时间，课程名，课程教室，老师名，是否实验)
        class_list = []
        for item in classes.json()["weekcalendarpojoList"]:
            class_info = {
                "课程时间": item["classString"],
                "课程名": item["className"],
                "课程教室": item["classRoom"],
                "老师": item["teacherName"],
                "是否实验": item["pkType"]
            }
            class_list.append(class_info)

        df = pd.DataFrame(class_list)
        df.to_excel("today_classes.xlsx", index=False)
        html = df.to_html(classes='styled-table',index=False)
        with open("today_classes.html", "w") as f:
            f.write("""
            <style>
            .styled-table {
                background-color: black;
                color: lawngreen;
                border-color: white;
                text-align: center;
            }
            .styled-table th {
                text-align: center;        
            }
            </style>
            """)
            f.write(html)
        webbrowser.open('file://' + os.path.realpath("today_classes.html"))

        return "获取成功"
    
    def get_class_table_tofile(self)->str:
        """获取这周课程表，如果今天是周五，则读到下周日
           返回excel文件和html文件。保存在本目录下
           并打开html文件
        """
        today = datetime.date.today()
        if today.weekday() == 5:
            end_date = today + datetime.timedelta((4 - today.weekday() + 7) % 7 + 7)
        else:
            end_date = today + datetime.timedelta((4 - today.weekday() + 7) % 7)
        date_range = pd.date_range(start=today, end=end_date)

        class_table = []
        class_info_initial = {
            "单双周": "",
            "周次": "",
        }

        for date in date_range:
            classes = self.session.post(self.Get_classes,data={"date":date.strftime("%Y-%m-%d")})
            class_info_initial["单双周"] = "单周" if classes.json()['dsWeek'] == 1 else "双周"
            class_info_initial["周次"] = classes.json()['week']
            for item in classes.json()["weekcalendarpojoList"]:
                class_info = {
                    "课程时间": item["classString"],
                    "课程地点": item["classRoom"],
                    "课程名": item["className"],
                    "老师": item["teacherName"],
                    "是否实验": item["pkType"],
                    "课程时间范围": item["weekSpan"],
                    "星期": date.weekday() + 1
                }
                class_info.update(class_info_initial)
                class_table.append(class_info)
        df = pd.DataFrame(class_table)
        writer = pd.ExcelWriter("class_tables.xlsx")
        for week in df["周次"].unique():
            for i in range(1,8):
                df_weekday = df[(df["星期"] == i) & (df["周次"] == week)]
                if df_weekday.empty:
                    df_weekday = pd.DataFrame({"今日无课": ["今日无课"]})
                else:
                    df[(df["星期"] == i) & (df["周次"] == week)].to_excel(writer, sheet_name=f"第{week}周_星期{i}", index=False)
            writer._save()
         
        # 将每个星期的数据写入html文件
        with open("class_table.html", "w") as f:
            f.write("""
            <style>
            .styled-table {
                background-color: black;
                color: lawngreen;
                border-color: white;
                text-align: center;
            }
            .styled-table th {
                text-align: center;        
            }
            </style>
            """)
            for week in df["周次"].unique():
                for i in range(1,8):
                    df_weekday = df[(df["星期"] == i) & (df["周次"] == week)]
                    if df_weekday.empty:        
                        f.write(f"<h1>第{week}周星期{i}</h1>")
                        f.write("<p>今日无课</p>")
                    else:
                        html = df_weekday.to_html(classes='styled-table',index=False)
                        f.write(f"<h1>第{week}周星期{i}</h1>")
                        f.write(html)
                        f.write("<br>")
        webbrowser.open('file://' + os.path.realpath("class_table.html"))
        return "获取成功"

    def get_classes(self,date:str = datetime.datetime.now().strftime("%Y-%m-%d")) -> list:
        """读取指定的课程情况，否则读取今天的课程
           返回一个列表，包含要求日期的所有课程信息"""
        classes = self.session.post(self.Get_classes,data={"date":date})
        if len(classes.json()["weekcalendarpojoList"]) == 0:
            return None
        #返回今天的课（课程时间，课程名，课程教室，老师名，是否实验)
        class_list = []
        for item in classes.json()["weekcalendarpojoList"]:
            class_info = {
                "class_time": item["classString"],
                "class_name": item["className"],
                "class_room": item["classRoom"],
                "class_teacher": item["teacherName"],
                "is_experiment": item["pkType"]
            }
            class_list.append(class_info)
        return class_list

    def get_grade_count(self)->dict:
        """获取班级姓名和平均学分绩点
           返回一个字典
        """
        grade_html = self.session.get(self.Get_grade)
        soup = BeautifulSoup(grade_html.text, 'html.parser')
        data_row = soup.find_all("tr")[3]
        data = [td.text for td in data_row.find_all("td")]
        grade_count = {
            "name":data[1],
            "class":data[2],
            "Gpa":data[6],
        }
        return grade_count
    
    def get_grade_from_semester(self,semester:str) -> dict:
        """获取某学期的成绩(学期的输入格式应为2022.1)
           返回一个字典，包含要求学期的所有课程及成绩情况
           字典demo
            {
                "course_term":"2022.1",
                "grade_info":{
                    "class_name":"高等数学",
                    "class_nature":"必修",
                    "class_credits":4,
                    "class_grade":90,
                }
            ……
            }
        """
        grade_html = self.session.get(self.Get_grade)
        tsemester = semester.replace(".","_")
        grade_from_semester_list = []
        soup = BeautifulSoup(grade_html.text, 'html.parser')

        pattern = re.compile(r'\b{}\b'.format(tsemester))
        ul_tags = soup.find_all("ul",class_=pattern)
        grade_from_semester_initial = {
            "course_term":semester,
            "grade_info":[]
        }
        for ul_tag in ul_tags:
            li_list = ul_tag.find_all("li")
            li_values = [li.text for li in li_list]
            grade_from_semester = {
                "class_name":li_values[1],
                "class_nature":li_values[2],
                "class_credits":li_values[4],
                "class_grade":li_values[5],
            }
            grade_from_semester_initial["grade_info"].append(grade_from_semester)
        return grade_from_semester_initial

    def get_grade_from_semester_zh(self,semester:str) -> dict:
    
        grade_html = self.session.get(self.Get_grade)
        tsemester = semester.replace(".","_")
        grade_from_semester_list = []
        soup = BeautifulSoup(grade_html.text, 'html.parser')

        pattern = re.compile(r'\b{}\b'.format(tsemester))
        ul_tags = soup.find_all("ul",class_=pattern)
        grade_from_semester_initial = {
            "课程学期":semester,
            "课程":[]
        }
        for ul_tag in ul_tags:
            li_list = ul_tag.find_all("li")
            li_values = [li.text for li in li_list]
            grade_from_semester = {
                "课程名":li_values[1],
                "课程性质":li_values[2],
                "学分":li_values[4],
                "成绩":li_values[5],
            }
            grade_from_semester_initial["课程"].append(grade_from_semester)
        return grade_from_semester_initial
        
    def get_grade_from_semester_tofile(self,semester:str) -> str:
        """获取某学期的成绩(学期的输入格式应为2022.1)
           将数据保存到excel文件和html文件,并打开html文件
           返回"获取成功"
        """
        grade_from_semester_list = self.get_grade_from_semester_zh(semester)
        print(grade_from_semester_list)
        data = grade_from_semester_list["课程"]
        df = pd.DataFrame(grade_from_semester_list["课程"])
        df.to_excel(f"{semester}_grades.xlsx", index=False)

        html = df.to_html(classes='styled-table',index=False)
        with open(f"{semester}_grades.html", "w") as f:
            f.write("""
            <style>
            .styled-table {
                background-color: black;
                color: lawngreen;
                border-color: white;
                text-align: center;
            }
            .styled-table th {
                text-align: center;        
            }
            </style>
            """)
            f.write(html)
        webbrowser.open('file://' + os.path.realpath(f"{semester}_grades.html"))
        return "获取成功"

    def __del__(self):
        if self.session:
            self.session.close()