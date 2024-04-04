RAW_RESPONSE_HEADER = "X-Stainless-Raw-Response"

ECJTU_DOMAIN = "ecjtu.edu.cn"
PORTAL_ECJTU_DOMAIN = f"http://portal.{ECJTU_DOMAIN}/dcp/index.jsp"
CAS_ECJTU_DOMAIN = f"cas.{ECJTU_DOMAIN}"
JWXT_ECJTU_DOMAIN = f"jwxt.{ECJTU_DOMAIN}"
PWD_ENC_URL = f"http://{CAS_ECJTU_DOMAIN}/cas/loginPasswdEnc"
ECJTU_LOGIN_URL = f"http://{CAS_ECJTU_DOMAIN}/cas/login"  # 智慧交大登录页
JWXT_LOGIN_URL = (
    f"https://{JWXT_ECJTU_DOMAIN}/stuMag/Login_dcpLogin.action"  # 教务系统登录页
)
ECJTU2JWXT_URL = f"http://{CAS_ECJTU_DOMAIN}/cas/login?service=https%3A%2F%2Fjwxt.ecjtu.edu.cn%2FstuMag%2FLogin_dcpLogin.action"  # 智慧交大登录教务系统 # noqa
GET_CLASSES_URL = f"https://{JWXT_ECJTU_DOMAIN}/Schedule/Weekcalendar_getTodayWeekcalendar.action"  # 获取课程信息(post) # noqa
GET_GPA_URL = f"https://{JWXT_ECJTU_DOMAIN}/scoreQuery/stuScoreQue_getStuScore.action?item=0401"  # 获取成绩信息(get) # noqa

GET_ELERTIVE_COURSE_URL_TEMPLATE = f"https://{JWXT_ECJTU_DOMAIN}/infoQuery/XKStu_findTerm.action"  # 获取选修课程信息(get) # noqa
