from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.requests import Request

from .pydantic import (
    AllSelectedDataPydantic,
    FailedDataPydantic,
    VerifyCodePydantic,
    LoginPydantic,
    PCPydantic,
    PEPydantic
)
from snatcher.db.mysql import (
    scd_querier,
    fd_querier,
    vc_querier,
    pe_querier,
    pc_querier
)


router = APIRouter(prefix='/manage')

SECRET = '410d5e58a1268d7c11552571b9c13dbf2e095f28f37fe3ed6e8149ca0e30abff'


def identity_validator(request: Request):
    token = request.headers.get('Authorization')
    if not token:
        return JSONResponse({'msg': '非法请求', 'success': 0}, status_code=401)
    try:
        jwt.decode(token, SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return JSONResponse({'msg': '身份已过期', 'success': 0}, status_code=401)
    except jwt.InvalidTokenError:
        return JSONResponse({'msg': '无效的凭证', 'success': 0}, status_code=401)


def delay_time(
    days=0,
    seconds=0,
    microseconds=0,
    milliseconds=0,
    minutes=0,
    hours=0,
    weeks=0
):
    now = datetime.now()
    utc_ctime = datetime.utcfromtimestamp(now.timestamp())  # use utc time
    time_delay = timedelta(days=days, seconds=seconds, microseconds=microseconds,
                           milliseconds=milliseconds, minutes=minutes,
                           hours=hours, weeks=weeks)
    return utc_ctime + time_delay


@router.get('/selected/count', response_model=int, tags=['查询所有已选课程信息数量'])
def get_all_selected_data_count(request: Request):
    response = identity_validator(request)
    if response:
        return response
    return scd_querier.count()


@router.get('/selected/{page}', response_model=list[AllSelectedDataPydantic], tags=['查询所有已选课程信息'])
def get_all_selected_data(page: int, request: Request):
    response = identity_validator(request)
    if response:
        return response
    return scd_querier.pagination_query(page)


@router.get('/failed/count', tags=['查询所有选课失败的数量'])
def get_failed_data_count(request: Request):
    response = identity_validator(request)
    if response:
        return response
    return fd_querier.count()


@router.get('/failed/{page}', tags=['查询所有失败选课信息'], response_model=list[FailedDataPydantic])
def get_failed_data(page: int, request: Request):
    response = identity_validator(request)
    if response:
        return response
    return fd_querier.pagination_query(page)


@router.get('/codes/count', tags=['查询所有验证码数量'])
def get_verify_code_count(request: Request):
    response = identity_validator(request)
    if response:
        return response
    return vc_querier.count()


@router.get('/codes/{page}', tags=['查询所有验证码'], response_model=list[VerifyCodePydantic])
def get_verify_code(page: int, request: Request):
    response = identity_validator(request)
    if response:
        return response
    return vc_querier.pagination_query(page)


@router.post('/codes', tags=['生成验证码'])
def create_verify_code(username: str, request: Request):
    response = identity_validator(request)
    if response:
        return response
    return vc_querier.insert(username)


@router.get('/pc/count', tags=['查询公选课总数'])
def get_pc_course_count(request: Request):
    response = identity_validator(request)
    if response:
        return response
    return pc_querier.count()


@router.get('/pe/count', tags=['查询体育课总数'])
def get_pe_course_count(request: Request):
    response = identity_validator(request)
    if response:
        return response
    return pe_querier.count()


@router.get('/pc/{page}', response_model=list[PCPydantic], tags=['查询公选课列表'])
def get_pc_course(request: Request, page: int = 1):
    response = identity_validator(request)
    if response:
        return response
    return pc_querier.pagination_query(page)


@router.get('/pe/{page}', response_model=list[PEPydantic], tags=['查询体育课列表'])
def get_pe_course(request: Request, page: int = 1):
    response = identity_validator(request)
    if response:
        return response
    return pe_querier.pagination_query(page)


@router.post('/login', tags=['超级管理员登录'])
def superuser_login(form: LoginPydantic):
    if form.username == 'rainbow' and form.password == '-+52th20040218*':
        exp = delay_time(seconds=60 * 60)
        token = jwt.encode({'username': form.username, 'exp': exp}, SECRET, algorithm='HS256')
        response = JSONResponse({'success': 1})
        response.headers.setdefault('Access-Control-Expose-Headers', 'Authorization')
        response.headers.setdefault('Authorization', token)
        return response
    return {'msg': '身份验证失败', 'success': 0}
