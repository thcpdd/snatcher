from fastapi import APIRouter

from .pydantic import (
    PCPydantic,
    PEPydantic,
    BookPEPydantic,
    BookPCPydantic
)
from snatcher import (
    async_public_choice,
    async_physical_education
)
from snatcher.db.mysql import (
    pe_querier,
    pc_querier,
    vc_querier
)
from snatcher.db.cache import judge_code_is_using


router = APIRouter(prefix='/vpn')


def check_verify_code(username: str, verify_code: str) -> int | dict:
    query = vc_querier.query(username, verify_code)
    if not query:
        return {'success': 0, 'msg': '无效的抢课码'}
    if query[0] == 1:
        return {'success': 0, 'msg': '该抢课码已被使用'}
    if judge_code_is_using(verify_code):
        return {'success': 0, 'msg': '该抢课码正在使用中'}
    return 0


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
async def book_pc_course(data: BookPCPydantic):
    problem = check_verify_code(data.username, data.verify_code)
    if problem:
        return problem
    goals = data.packing_data()
    await async_public_choice(goals, **data.users())
    return {'success': 1}


@router.post('/pe', tags=['预约体育课'])
async def book_pe_course(data: BookPEPydantic):
    problem = check_verify_code(data.username, data.verify_code)
    if problem:
        return problem
    goals = data.packing_data()
    await async_physical_education(goals, **data.users())
    return {'success': 1}
