import json
from typing import Generic, Optional, TypeVar, Union

import httpx
import requests
from bs4 import BeautifulSoup
from httpx import URL, Timeout
from loguru import logger

from ecjtu import crud, models
from ecjtu.constants import (
    CAS_ECJTU_DOMAIN,
    ECJTU2JWXT_URL,
    ECJTU_LOGIN_URL,
    JWXT_LOGIN_URL,
    PWD_ENC_URL,
)

_HttpxClientT = TypeVar("_HttpxClientT", bound=Union[httpx.Client, httpx.AsyncClient])
_RequestSessionT = TypeVar("_RequestSessionT", bound=Union[requests.Session])


def get_enc_password(original_pwd: str) -> str:
    """Get encrypted password

    Args:
        original_pwd(str): Original password

    Returns:
        str: Encrypted password
    """
    enc_response = httpx.post(PWD_ENC_URL, data={"pwd": original_pwd})

    _ = enc_response.content.decode("utf8").replace("'", '"')
    return json.loads(_)["passwordEnc"]


class BaseClient(Generic[_RequestSessionT]):
    _client: _RequestSessionT
    _version: str
    _base_url: URL
    max_retries: int
    timeout: Union[float, Timeout, None]
    _limits: httpx.Limits
    _strict_response_validation: bool
    _idempotency_header: str | None


class ECJTU:
    """
    ECJTU client
    """

    def __init__(
        self, stud_id: str, password: str, client: Optional[requests.Session] = None
    ) -> None:
        """Initialize ECJTU client.

        Args:
            stud_id(str): Student ID
            password(str): Password
            client(Optional[requests.Session]): Requests session
        """
        self.stud_id: str = stud_id
        self.password: str = password
        self._enc_password: Optional[str] = None
        self._client: requests.Session = client or requests.Session()

        self.login()

        self.scheduled_courses = crud.ScheduledCourseCRUD(self._client)
        self.scores = crud.ScoreCRUD(self._client)
        self.gpa = crud.GPACRUD(self._client)

    @property
    def enc_password(self) -> str:
        """Get encrypted password

        Returns:
            str: Encrypted password
        """
        if self._enc_password is None:
            self._enc_password = get_enc_password(self.password)
        return self._enc_password

    def login(self) -> None:
        """Login to ECJTU system and update the client session."""
        logger.info("Logging in")
        requests.packages.urllib3.disable_warnings()

        login_payload = {
            "username": self.stud_id,
            "password": self.enc_password,
            "service": "http://portal.ecjtu.edu.cn/dcp/index.jsp",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Host": CAS_ECJTU_DOMAIN,
        }
        response = self._client.get(ECJTU_LOGIN_URL, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        login_payload["lt"] = soup.find("input", {"name": "lt"})["value"]

        headers_append = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": ECJTU_LOGIN_URL,
        }
        headers.update(headers_append)
        response = self._client.post(
            ECJTU_LOGIN_URL, data=login_payload, headers=headers, allow_redirects=False
        )

        if "CASTGC" not in response.cookies:
            raise ValueError("Error in account or password")

        self._client.get(
            JWXT_LOGIN_URL, headers=headers, allow_redirects=False, verify=False
        )

        response_url = self._client.get(ECJTU2JWXT_URL, allow_redirects=False)

        result = self._client.get(response_url.headers["location"])

        if result.status_code != 200:
            raise ValueError(
                f"Error in JWXT system, login failed: {result.status_code}"
            )

        logger.info("Login successful")
