from pydantic import BaseModel


class BookCoursePydantic(BaseModel):
    email: str
    username: str
    password: str
    verify_code: str


class CoursePydantic(BaseModel):
    id: int
    course_id: str
    course_name: str


class PEPydantic(CoursePydantic):
    grade: int


class PCPydantic(CoursePydantic):
    course_no: str


class BookPEPydantic(BookCoursePydantic):
    courses: list[PEPydantic]


class BookPCPydantic(BookCoursePydantic):
    courses: list[PCPydantic]
