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
    verify_code = check_verify_code(data.username, data.verify_code)
    if not verify_code:
        return {'success': 0, 'msg': '无效的抢课码'}
    if verify_code[0] == 1:
        return {'success': 0, 'msg': '该抢课码已被使用'}
    goals = data.packing_data()
    public_choice(goals, **data.users())
    return {'success': 1}


@router.post('/pe', tags=['预约体育课'])
def book_pe_course(data: BookPEPydantic):
    verify_code = check_verify_code(data.username, data.verify_code)
    if not verify_code:
        return {'success': 0, 'msg': '无效的抢课码'}
    if verify_code[0] == 1:
        return {'success': 0, 'msg': '该抢课码已被使用'}
    goals = data.packing_data()
    physical_education(goals, **data.users())
    return {'success': 1}
