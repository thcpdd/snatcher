from fastapi import APIRouter

from .pydantic import (
    PCPydantic,
    PEPydantic,
    BookPEPydantic,
    BookPCPydantic
)
from snatcher import (
    public_choice,
    physical_education
)
from snatcher.db.mysql import (
    query_all_pe_course,
    query_all_pc_course,
    query_pe_course_count,
    query_pc_course_count,
    query_pc_course,
    query_pe_course,
    check_verify_code
)


router = APIRouter(prefix='/vpn')


@router.get('/pc/count', tags=['查询公选课总数'])
def get_pc_course_count():
    return query_pc_course_count()


@router.get('/pe/count', tags=['查询体育课总数'])
def get_pe_course_count():
    return query_pe_course_count()


@router.get('/pc/{page}', response_model=list[PCPydantic], tags=['查询公选课列表'])
def get_pc_course(page: int = 1):
    return query_all_pc_course(page)


@router.get('/pe/{page}', response_model=list[PEPydantic], tags=['查询体育课列表'])
def get_pe_course(page: int = 1):
    return query_all_pe_course(page)


@router.get('/pe', tags=['搜索体育课'], response_model=list[PEPydantic])
def search_pe_course(keyword: str):
    return query_pe_course(keyword)


@router.get('/pc', tags=['搜索公选课'], response_model=list[PCPydantic])
def search_pc_course(keyword: str):
    return query_pc_course(keyword)


@router.post('/pc', tags=['预约公选课'])
def book_pc_course(data: BookPCPydantic):
    if not check_verify_code(data.username, data.verify_code):
        return {'success': 0, 'msg': '无效的抢课码'}
    conditions = [course.course_no for course in data.courses]
    public_choice(data.username, data.password, conditions, data.email)
    return {'success': 1}


@router.post('/pe', tags=['预约体育课'])
def book_pe_course(data: BookPEPydantic):
    if not check_verify_code(data.username, data.verify_code):
        return {'success': 0, 'msg': '无效的抢课码'}
    conditions = [course.course_name for course in data.courses]
    physical_education(data.username, data.password, conditions, data.email)
    return {'success': 1}
