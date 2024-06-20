from datetime import datetime

from pydantic import BaseModel


class AllSelectedDataValidator(BaseModel):
    id: int
    username: str
    email: str
    course_name: str
    created_at: datetime
    log_key: str


class FailedDataValidator(BaseModel):
    id: int
    username: str
    port: int
    course_name: str
    created_at: datetime
    log_key: str
    failed_reason: str


class VerifyCodeValidator(BaseModel):
    id: int
    username: str
    is_used: int
    verify_code: str
    create_at: datetime


class LoginValidator(BaseModel):
    username: str
    password: str


class CourseValidator(BaseModel):
    id: int
    course_id: str
    course_name: str
    study_year: int
    term: str


class PEValidator(CourseValidator):
    grade: int


class PCValidator(CourseValidator):
    course_no: str
    period: int
