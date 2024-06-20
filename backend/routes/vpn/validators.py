from pydantic import BaseModel


class BookCourseValidator(BaseModel):
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


class CourseValidator(BaseModel):
    id: int
    course_id: str
    course_name: str


class PEValidator(CourseValidator):
    grade: int


class PCValidator(CourseValidator):
    course_no: str


class BookPEValidator(BookCourseValidator):
    courses: list[PEValidator]

    def packing_data(self) -> list[tuple[str, str]]:
        return [(course.course_name, course.course_id) for course in self.courses]


class BookPCValidator(BookCourseValidator):
    courses: list[PCValidator]

    def packing_data(self) -> list[tuple[str, str]]:
        return [(course.course_name, course.course_id) for course in self.courses]
