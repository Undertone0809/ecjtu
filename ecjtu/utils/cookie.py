from typing import Optional

import httpx
from httpx._types import CookieTypes


def cookies_tolist(cookies: Optional[CookieTypes]):
    cookies_list = []
    for cookie in cookies.jar:
        dict = {
            "name": cookie.name,
            "value": cookie.value,
            "domain": cookie.domain,
        }
        cookies_list.append(dict)
    return cookies_list


def list_tocookie(cookies_list: list):
    cookies = httpx.Cookies()
    for cookie in cookies_list:
        cookies.set(**cookie)
    return cookies
