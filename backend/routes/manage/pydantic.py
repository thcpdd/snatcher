from datetime import datetime

from pydantic import BaseModel


class AllSelectedDataPydantic(BaseModel):
    id: int
    username: str
    email: str
    course_name: str
    created_at: datetime
    log_key: str


class FailedDataPydantic(BaseModel):
    id: int
    username: str
    port: int
    course_name: str
    created_at: datetime
    log_key: str
    failed_reason: str


class VerifyCodePydantic(BaseModel):
    id: int
    username: str
    is_used: int
    verify_code: str
    create_at: datetime


class LoginPydantic(BaseModel):
    username: str
    password: str
