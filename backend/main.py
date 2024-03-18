from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .pydantic import (
    PCPydantic,
    PEPydantic,
    PEPostPydantic,
    PCPostPydantic
)
from snatcher.db.mysql import (
    query_all_pe_course,
    query_all_pc_course,
    query_pe_course_count,
    query_pc_course_count,
    query_pc_course,
    query_pe_course,
)

app = FastAPI()
router = APIRouter(prefix='/vpn')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


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


@router.get('/pe', tags=['搜索体育课'])
def search_pe_course(keyword: str):
    return query_pe_course(keyword)


@router.get('/pc', tags=['搜索公选课'])
def search_pc_course(keyword: str):
    return query_pc_course(keyword)


@router.post('/pc', tags=['预约公选课'])
def book_pc_course(data: PCPostPydantic):
    print(data)
    return 1


@router.post('/pe', tags=['预约体育课'])
def book_pe_course(data: PEPostPydantic):
    print(data)
    return 1


app.include_router(router)
