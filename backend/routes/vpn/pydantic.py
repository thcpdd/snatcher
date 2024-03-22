from pydantic import BaseModel


class BookCoursePydantic(BaseModel):
    email: str
    username: str
    password: str
    verify_code: str

    def users(self) -> dict:
        return {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "verify_code": self.verify_code,
        }


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

    def packing_data(self) -> list[tuple[str, str]]:
        return [(course.course_name, course.course_id) for course in self.courses]


class BookPCPydantic(BookCoursePydantic):
    courses: list[PCPydantic]

    def packing_data(self) -> list[tuple[str, str]]:
        return [(course.course_name, course.course_id) for course in self.courses]
