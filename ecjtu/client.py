import json
import os
import typing
from typing import Generic, Optional, TypeVar, Union

import httpx
from bs4 import BeautifulSoup
from httpx import USE_CLIENT_DEFAULT, Response, Timeout
from httpx._client import UseClientDefault  # noqa
from httpx._types import (  # noqa
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestExtensions,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)

from ecjtu import crud
from ecjtu.constants import (
    CAS_ECJTU_DOMAIN,
    ECJTU2JWXT_URL,
    ECJTU_LOGIN_URL,
    JWXT_LOGIN_URL,
    PORTAL_ECJTU_DOMAIN,
    PWD_ENC_URL,
)
from ecjtu.utils.logger import logger

_HttpxClientT = TypeVar("_HttpxClientT", bound=Union[httpx.Client, httpx.AsyncClient])


def _get_enc_password(original_pwd: str) -> str:
    """Get encrypted password

    Args:
        original_pwd(str): Original password

    Returns:
        str: Encrypted password
    """
    enc_response = httpx.post(PWD_ENC_URL, data={"pwd": original_pwd})

    _ = enc_response.content.decode("utf8").replace("'", '"')
    return json.loads(_)["passwordEnc"]


class BaseClient(Generic[_HttpxClientT]):
    _version: str
    max_retries: int = 5
    timeout: Union[float, Timeout, None]
    _limits: httpx.Limits
    cookies: httpx.Cookies

    @property
    def has_login(self) -> bool:
        return "CASTGC" in self.cookies


class ECJTU(BaseClient[httpx.Client], httpx.Client):
    def __init__(
        self, stud_id: Optional[str] = None, password: Optional[str] = None, **kwargs
    ) -> None:
        """Initialize ECJTU client.

        Args:
            stud_id(str): Student ID
            password(str): Password
        """
        super().__init__(verify=False, **kwargs)

        self.stud_id: str = stud_id or os.environ.get("ECJTU_STUDENT_ID")
        self.password: str = password or os.environ.get("ECJTU_PASSWORD")
        self.enc_password: str = _get_enc_password(self.password)

        self.scheduled_courses = crud.ScheduledCourseCRUD(self)
        self.scores = crud.ScoreCRUD(self)
        self.gpa = crud.GPACRUD(self)
        self.elective_courses = crud.ElectiveCourseCRUD(self)

    def post(
        self,
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: typing.Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
        current_retries: int = 0,
    ) -> Response:
        """Wrap the httpx post method to handle retries and check login status.

        Addition Args:
            current_retries(int): Current retries count
        """
        if not self.has_login:
            self.login()

        params = dict(
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        try:
            return super().post(url, **params)

        except httpx.HTTPStatusError as e:
            if current_retries >= self.max_retries:
                raise e

            return self.post(url, **params, current_retries=current_retries + 1)

    def get(
        self,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
        current_retries: int = 0,
    ) -> Response:
        """Wrap the httpx get method to handle retries and check login status.

        Addition Args:
            current_retries(int): Current retries count
        """
        if not self.has_login:
            self.login()

        _params = dict(
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        try:
            return super().get(url, **_params)

        except httpx.HTTPStatusError as e:
            if current_retries >= self.max_retries:
                raise e

            return self.get(url, **_params, current_retries=current_retries + 1)

    def login(self) -> None:
        """Login to ECJTU system and update the client session."""
        logger.info("Logging in")

        login_payload = {
            "username": self.stud_id,
            "password": self.enc_password,
            "service": PORTAL_ECJTU_DOMAIN,
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                  (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Host": CAS_ECJTU_DOMAIN,
        }
        response = super().get(ECJTU_LOGIN_URL, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        login_payload["lt"] = soup.find("input", {"name": "lt"})["value"]

        headers_append = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": ECJTU_LOGIN_URL,
        }
        headers.update(headers_append)
        response = super().post(
            ECJTU_LOGIN_URL,
            data=login_payload,
            headers=headers,
        )

        if "CASTGC" not in response.cookies:
            raise ValueError("Error in account or password")

        super().get(JWXT_LOGIN_URL, headers=headers)

        response_url = super().get(ECJTU2JWXT_URL)

        result = super().get(response_url.headers["location"], follow_redirects=True)

        if result.status_code != 200:
            raise ValueError(
                f"Error in JWXT system, login failed: {result.status_code}"
            )

        logger.info("Login successful")

    def start_api_server(self, port: int = 8000):
        # TODO: Start a FastAPI server
        pass


class AsyncECJTU(BaseClient[httpx.AsyncClient], httpx.AsyncClient):
    def __init__(self, stud_id: str, password: str, **kwargs) -> None:
        """Initialize ECJTU client.

        Args:
            stud_id(str): Student ID
            password(str): Password
        """
        super().__init__(verify=False, **kwargs)

        self.stud_id: str = stud_id or os.environ.get("ECJTU_STUDENT_ID")
        self.password: str = password or os.environ.get("ECJTU_PASSWORD")
        self.enc_password: str = _get_enc_password(self.password)

        self.scheduled_courses = crud.AsyncScheduledCourseCRUD(self)
        self.scores = crud.AsyncScoreCRUD(self)
        self.gpa = crud.AsyncGPACRUD(self)
        self.elective_courses = crud.AsyncElectiveCourseCRUD(self)

    async def post(
        self,
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: typing.Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
        current_retries: int = 0,
    ) -> Response:
        """Wrap the httpx post method to handle retries and check login status.

        Addition Args:
            current_retries(int): Current retries count
        """
        if not self.has_login:
            await self.login()

        params = dict(
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        try:
            return await super().post(url, **params)

        except httpx.HTTPStatusError as e:
            if current_retries >= self.max_retries:
                raise e

            return await self.post(url, **params, current_retries=current_retries + 1)

    async def get(
        self,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
        current_retries: int = 0,
    ) -> Response:
        """Wrap the httpx get method to handle retries and check login status.

        Addition Args:
            current_retries(int): Current retries count
        """
        if not self.has_login:
            await self.login()

        _params = dict(
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        try:
            return await super().get(url, **_params)

        except httpx.HTTPStatusError as e:
            if current_retries >= self.max_retries:
                raise e

            return await self.get(url, **_params, current_retries=current_retries + 1)

    async def login(self) -> None:
        """Login to ECJTU system and update the client session."""
        logger.info("Logging in")

        login_payload = {
            "username": self.stud_id,
            "password": self.enc_password,
            "service": PORTAL_ECJTU_DOMAIN,
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                  (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Host": CAS_ECJTU_DOMAIN,
        }
        response = await super().get(ECJTU_LOGIN_URL, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        login_payload["lt"] = soup.find("input", {"name": "lt"})["value"]

        headers_append = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": ECJTU_LOGIN_URL,
        }
        headers.update(headers_append)
        response = await super().post(
            ECJTU_LOGIN_URL,
            data=login_payload,
            headers=headers,
        )

        if "CASTGC" not in response.cookies:
            raise ValueError("Error in account or password")

        await super().get(JWXT_LOGIN_URL, headers=headers)

        response_url = await super().get(ECJTU2JWXT_URL)

        result = await super().get(
            response_url.headers["location"], follow_redirects=True
        )

        if result.status_code != 200:
            raise ValueError(
                f"Error in JWXT system, login failed: {result.status_code}"
            )

        logger.info("Login successful")

    async def start_api_server(self):
        # TODO: Start a FastAPI server
        pass
