from pydantic import BaseModel


class PostCoursePydantic(BaseModel):
    email: str
    username: str
    password: str


class PEPydantic(BaseModel):
    id: int
    course_id: str
    course_name: str
    grade: int


class PCPydantic(BaseModel):
    course_id: str
    course_name: str
    course_no: str
    id: int


class PEPostPydantic(PostCoursePydantic):
    courses: list[PEPydantic]


class PCPostPydantic(PostCoursePydantic):
    courses: list[PCPydantic]
