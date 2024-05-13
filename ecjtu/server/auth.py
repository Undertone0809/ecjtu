import base64
import datetime

import httpx
from cushy_storage import CushyOrmCache

from ecjtu.client import ECJTU
from ecjtu.server import schema
from ecjtu.utils.cookie import cookies_tolist, list_tocookie
from ecjtu.utils.logger import get_path


def encode_data(data: str) -> str:
    """encode to string

    Args:
        data (str): string to encode

    Returns:
        str: encoded string
    """
    return base64.b64encode(data.encode()).decode()


def decode_data(encoded_data: str) -> str:
    """decode to string

    Args:
        encoded_data (str): encoded string

    Returns:
        str: decoded string
    """
    return base64.b64decode(encoded_data.encode()).decode()


def create_tokens(stud_id: str, pwd: str) -> tuple[str, str]:
    """create access_token and refresh_token

    Args:
        stud_id (str): student id
        pwd (str): password

    Returns:
        tuple[str, str]: access_token and refresh_token
    """
    access_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=60
    )
    access_data = f"{stud_id}:access_token:{access_time}"
    refresh_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        days=7
    )
    refresh_data = f"{stud_id}:{pwd}:{refresh_time}"

    access_token = encode_data(access_data)
    refresh_token = encode_data(refresh_data)
    client = ECJTU(stud_id, pwd)
    try:
        client.login()
    except Exception as e:
        raise e

    cookie_list = cookies_tolist(client.cookies)
    stud_file = CushyOrmCache(get_path())
    stud = stud_file.query("FileAuth").filter(stud_id=stud_id).first()

    # if not exist, create a new one
    if not stud:
        stud = schema.FileAuth(stud_id, access_token, cookie_list)
        stud_file.add(stud)
        return access_token, refresh_token
    # update the old one
    stud.cookie = cookie_list
    stud.token = access_token
    stud_file.update_obj(stud)
    return access_token, refresh_token


def refresh_access_token(refresh_token: str) -> str:
    """refresh access_token

    Args:
        refresh_token (str): refresh_token

    Returns:
        str: access_token

    Raises:
        Exception: if token is invalid or expired
    """
    data = decode_data(refresh_token)
    print(data)
    stud_id = data.split(":")[0]
    pwd = data.split(":")[1]
    token_time = data.split(":")[2]

    expire_time = datetime.datetime.fromisoformat(token_time)
    expire_time = expire_time.replace(tzinfo=datetime.timezone.utc)
    current_time = datetime.datetime.now(datetime.timezone.utc)

    if current_time > expire_time:
        raise Exception("令牌已过期，请重新登录")
    else:
        try:
            create_tokens(stud_id, pwd)
        except Exception:
            raise Exception("令牌有误，请重新登录")
        return create_tokens(stud_id, pwd)[0]


def get_stud_id(access_token: str) -> str:
    """get stud_id from access_token

    Args:
        access_token (str): access_token

    Returns:
        str: stud_id
    """
    try:
        data = decode_data(access_token)
        stud_file = CushyOrmCache(get_path())
        stud = stud_file.query("FileAuth").filter(token=access_token).first()
        if not stud:
            raise Exception("无效令牌")
    except Exception:
        raise Exception("无效令牌")
    stud_id = data.split(":")[0]
    token_time = data.split(":")[2]

    expire_time = datetime.datetime.fromisoformat(token_time)
    expire_time = expire_time.replace(tzinfo=datetime.timezone.utc)
    current_time = datetime.datetime.now(datetime.timezone.utc)

    if current_time > expire_time:
        raise Exception("令牌已过期，请刷新")
    return stud_id


def get_cookie(stud_id: str) -> httpx.Cookies:
    """get cookie from stud_id

    Args:
        stud_id (str): stud_id

    Returns:
        httpx.Cookies: cookies
    """
    stud_file = CushyOrmCache(get_path())
    stud = stud_file.query("FileAuth").filter(stud_id=stud_id).first()
    cookies = list_tocookie(stud.cookie)
    return cookies
