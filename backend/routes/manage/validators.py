from datetime import datetime

from pydantic import BaseModel, Field

from backend.utils.validators import ObjectId, DatetimeValidator


class SubmittedValidator(DatetimeValidator):
    row_id: ObjectId = Field(default_factory=ObjectId, alias='_id')
    username: str
    email: str
    course_name: str
    updated_at: datetime
    log_key: str
    success: int


class FailureValidator(DatetimeValidator):
    row_id: ObjectId = Field(default_factory=ObjectId, alias='_id')
    username: str
    port: int
    course_name: str
    created_at: datetime
    log_key: str
    reason: str


class EnergyValidator(DatetimeValidator):
    row_id: ObjectId = Field(default_factory=ObjectId, alias='_id')
    username: str
    status: str
    fuel: str
    created_at: datetime


class LoginValidator(BaseModel):
    username: str
    password: str


class CourseValidator(BaseModel):
    row_id: ObjectId = Field(default_factory=ObjectId, alias='_id')
    course_id: str
    course_name: str
    study_year: int
    term: int


class PEValidator(CourseValidator):
    grade: int


class PCValidator(CourseValidator):
    course_no: str
    period: int
