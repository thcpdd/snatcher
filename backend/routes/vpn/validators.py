from typing import Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class CourseTypeEnum(Enum):
    pc = '10'
    pe = '05'


class CourseValidator(BaseModel):
    course_id: str
    course_name: str
    jxb_id: str
    jxbmc: Optional[str] = None


class PEValidator(CourseValidator):
    grade: int


class PCValidator(CourseValidator):
    pass


class BookCourseValidator(BaseModel):
    email: EmailStr
    username: str
    password: Optional[str] = ''
    cookie: Optional[str] = ''
    port: Optional[str] = ''
    fuel: str = Field(..., pattern=r'^[A-Za-z0-9/+]{67}=$')
    courses: list[PEValidator | PCValidator]
    course_type: str = Field(..., pattern=r'^(pc|pe)$')
    token: str  # reCAPTCHA v3 token

    def packing_data(self) -> list[tuple[str, str, str]]:
        return [(course.course_name, course.course_id, course.jxb_id) for course in self.courses]
