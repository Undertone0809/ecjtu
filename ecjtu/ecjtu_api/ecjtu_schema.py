from pydantic import BaseModel, Field


class UserLoginSchema(BaseModel):
    stud_id: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
