from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request

from .validators import (
    AllSelectedDataValidator,
    FailedDataValidator,
    VerifyCodeValidator,
    LoginValidator,
    PCValidator,
    PEValidator
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
        raise HTTPException(401, detail={'msg': '非法请求', 'success': 0})
    try:
        jwt.decode(token, SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail={'msg': '身份已过期', 'success': 0})
    except jwt.InvalidTokenError:
        raise HTTPException(401, {'msg': '无效的凭证', 'success': 0})


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


@router.get(
    '/selected/count',
    response_model=int,
    tags=['查询所有已选课程信息数量'],
    dependencies=[Depends(identity_validator)]
)
def get_all_selected_data_count():
    return scd_querier.count()


@router.get(
    '/selected/{page}',
    response_model=list[AllSelectedDataValidator],
    tags=['查询所有已选课程信息'],
    dependencies=[Depends(identity_validator)]
)
def get_all_selected_data(page: int):
    return scd_querier.pagination_query(page)


@router.get(
    '/failed/count',
    tags=['查询所有选课失败的数量'],
    dependencies=[Depends(identity_validator)]
)
def get_failed_data_count():
    return fd_querier.count()


@router.get(
    '/failed/{page}',
    tags=['查询所有失败选课信息'],
    response_model=list[FailedDataValidator],
    dependencies=[Depends(identity_validator)]
)
def get_failed_data(page: int):
    return fd_querier.pagination_query(page)


@router.get(
    '/codes/count',
    tags=['查询所有验证码数量'],
    dependencies=[Depends(identity_validator)]
)
def get_verify_code_count():
    return vc_querier.count()


@router.get(
    '/codes/{page}',
    tags=['查询所有验证码'],
    response_model=list[VerifyCodeValidator],
    dependencies=[Depends(identity_validator)]
)
def get_verify_code(page: int):
    return vc_querier.pagination_query(page)


@router.post(
    '/codes',
    tags=['生成验证码'],
    dependencies=[Depends(identity_validator)]
)
def create_verify_code(username: str):
    return vc_querier.insert(username)


@router.get(
    '/pc/count',
    tags=['查询公选课总数'],
    dependencies=[Depends(identity_validator)]
)
def get_pc_course_count():
    return pc_querier.count()


@router.get(
    '/pe/count',
    tags=['查询体育课总数'],
    dependencies=[Depends(identity_validator)]
)
def get_pe_course_count():
    return pe_querier.count()


@router.get(
    '/pc/{page}',
    response_model=list[PCValidator],
    tags=['查询公选课列表'],
    dependencies=[Depends(identity_validator)]
)
def get_pc_course(page: int = 1):
    return pc_querier.pagination_query(page)


@router.get(
    '/pe/{page}',
    response_model=list[PEValidator],
    tags=['查询体育课列表'],
    dependencies=[Depends(identity_validator)]
)
def get_pe_course(page: int = 1):
    return pe_querier.pagination_query(page)


@router.post('/login', tags=['超级管理员登录'])
def superuser_login(form: LoginValidator):
    if form.username == 'rainbow' and form.password == '-+52th20040218*':
        exp = delay_time(seconds=60 * 60)
        token = jwt.encode({'username': form.username, 'exp': exp}, SECRET, algorithm='HS256')
        response = JSONResponse({'success': 1})
        response.headers.setdefault('Access-Control-Expose-Headers', 'Authorization')
        response.headers.setdefault('Authorization', token)
        return response
    return {'msg': '身份验证失败', 'success': 0}
