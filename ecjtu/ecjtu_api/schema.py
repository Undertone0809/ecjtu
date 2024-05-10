from typing import Dict, List, Optional

from cushy_storage import BaseORMModel, CushyOrmCache
from pydantic import BaseModel, Field


class UserLoginSchema(BaseModel):
    stud_id: str = Field(..., min_length=1, description="学号")
    password: str = Field(..., min_length=1, description="密码")


class FileAuth(BaseORMModel):
    def __init__(
        self,
        stud_id: Optional[str] = None,
        token: str = None,
        cookie: Optional[List[Dict]] = None,
    ) -> None:
        super().__init__()
        self.stud_id = stud_id
        self.token = token
        self.cookie = cookie
