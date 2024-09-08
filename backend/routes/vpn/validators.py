from typing import Optional
from enum import Enum

from pydantic import BaseModel, EmailStr


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
    password: str
    fuel: str
    courses: list[PEValidator | PCValidator]
    course_type: str

    def packing_data(self) -> list[tuple[str, str]]:
        return [(course.course_name, course.course_id) for course in self.courses]
