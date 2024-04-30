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
    pe_querier,
    pc_querier,
    vc_querier
)


router = APIRouter(prefix='/vpn')


@router.get('/pc/count', tags=['查询公选课总数'])
def get_pc_course_count():
    return pc_querier.count()


@router.get('/pe/count', tags=['查询体育课总数'])
def get_pe_course_count():
    return pe_querier.count()


@router.get('/pc/{page}', response_model=list[PCPydantic], tags=['查询公选课列表'])
def get_pc_course(page: int = 1):
    return pc_querier.pagination_query(page)


@router.get('/pe/{page}', response_model=list[PEPydantic], tags=['查询体育课列表'])
def get_pe_course(page: int = 1):
    return pe_querier.pagination_query(page)


@router.get('/pe', tags=['搜索体育课'], response_model=list[PEPydantic])
def search_pe_course(keyword: str):
    return pe_querier.like_query(keyword)


@router.get('/pc', tags=['搜索公选课'], response_model=list[PCPydantic])
def search_pc_course(keyword: str):
    return pc_querier.like_query(keyword)


@router.post('/pc', tags=['预约公选课'])
def book_pc_course(data: BookPCPydantic):
    verify_code = vc_querier.query(data.username, data.verify_code)
    if not verify_code:
        return {'success': 0, 'msg': '无效的抢课码'}
    if verify_code[0] == 1:
        return {'success': 0, 'msg': '该抢课码已被使用'}
    goals = data.packing_data()
    public_choice(goals, **data.users())
    return {'success': 1}


@router.post('/pe', tags=['预约体育课'])
def book_pe_course(data: BookPEPydantic):
    verify_code = vc_querier.query(data.username, data.verify_code)
    if not verify_code:
        return {'success': 0, 'msg': '无效的抢课码'}
    if verify_code[0] == 1:
        return {'success': 0, 'msg': '该抢课码已被使用'}
    goals = data.packing_data()
    physical_education(goals, **data.users())
    return {'success': 1}
