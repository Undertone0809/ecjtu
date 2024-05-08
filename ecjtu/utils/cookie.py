from typing import Optional

import httpx
from httpx._types import CookieTypes


def cookies_tolist(cookies: Optional[CookieTypes]) -> list:
    cookies_list = []
    for cookie in cookies.jar:
        cookie_dict = {
            "name": cookie.name,
            "value": cookie.value,
            "domain": cookie.domain,
        }
        cookies_list.append(cookie_dict)
    return cookies_list


def list_tocookie(cookies_list: list) -> httpx.Cookies:
    cookies = httpx.Cookies()
    for cookie in cookies_list:
        cookies.set(**cookie)
    return cookies
