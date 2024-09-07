import asyncio

from fastapi import APIRouter, Path, Query
from redis.asyncio import Redis as AIORedis

from .validators import PCValidator, PEValidator, BookPEValidator, BookPCValidator, CourseTypeEnum
from backend.response import SnatcherResponse, ResponseCodes
from snatcher import async_public_choice, async_physical_education
from snatcher.storage.mongo import get_fuel_status, collections, get_security_key, BSONObjectId
from snatcher.utils.hashlib import decrypt_fuel
from snatcher.storage.cache import export_progress
from snatcher.conf import settings


router = APIRouter(prefix='/vpn', tags=['VPN'])


def check_fuel(username: str, fuel: str) -> tuple[int, str]:
    try:
        status = get_fuel_status(username, fuel)
    except Exception as e:
        print('fuel解码失败', e)
        return ResponseCodes.INVALID_FUEL
    if not status:
        return ResponseCodes.INVALID_FUEL
    if status == 'used':
        return ResponseCodes.FUEL_WAS_USED
    if status == 'using':
        return ResponseCodes.FUEL_IS_USING
    return ResponseCodes.OK


@router.get('/pc/{page}', summary='查询公选课')
def get_pc_course(page: int = Path(ge=1)):
    pc_collection = collections['pc']
    cursor, total = pc_collection.query(page)
    results = []
    for row in cursor:
        validator = PCValidator(**row)
        results.append(validator.model_dump())
    return SnatcherResponse(ResponseCodes.OK, {'results': results, 'total': total})


@router.get('/pe/{page}', summary='查询体育课')
def get_pe_course(page: int = Path(ge=1)):
    pe_collection = collections['pe']
    cursor, total = pe_collection.query(page)
    results = []
    for row in cursor:
        validator = PEValidator(**row)
        results.append(validator.model_dump())
    return SnatcherResponse(ResponseCodes.OK, {'results': results, 'total': total})


@router.get('/pe', summary='搜索体育课')
def search_pe_course(keyword: str):
    pe_collection = collections['pe']
    cursor, total = pe_collection.query(1, course_name={'$regex': keyword, '$options': 'i'})
    results = []
    for data in cursor:
        validator = PEValidator(**data)
        results.append(validator.model_dump())
    return SnatcherResponse(ResponseCodes.OK, {'results': results, 'total': total})


@router.get('/pc', summary='搜索公选课')
def search_pc_course(keyword: str):
    pc_collection = collections['pc']
    results = []
    cursor, total = pc_collection.query(1, course_name={'$regex': keyword, '$options': 'i'})
    for data in cursor:
        validator = PCValidator(**data)
        results.append(validator.model_dump())
    return SnatcherResponse(ResponseCodes.OK, {'results': results, 'total': total})


@router.post('/pc', summary='预约公选课')
async def book_pc_course(data: BookPCValidator):
    message_tuple = check_fuel(data.username, data.fuel)
    if message_tuple[0] != 1:
        return SnatcherResponse(message_tuple)
    goals = data.packing_data()
    users = data.model_dump(exclude={'courses'})
    await async_public_choice(goals, **users)
    return SnatcherResponse(ResponseCodes.OK)


@router.post('/pe', summary='预约体育课')
async def book_pe_course(data: BookPEValidator):
    message_tuple = check_fuel(data.username, data.fuel)
    if message_tuple[0] != 1:
        return SnatcherResponse(message_tuple)
    goals = data.packing_data()
    users = data.model_dump(exclude={'courses'})
    await async_physical_education(goals, **users)
    return SnatcherResponse(ResponseCodes.OK)


@router.get('/user/progress', summary='查询用户选课进度')
def select_course_progress(fuel: str = Query(pattern=r'^[A-Za-z0-9/+]{67}=$')):
    key = get_security_key('fuel')
    try:
        fuel_id = decrypt_fuel(fuel, key)
    except Exception as e:
        print('fuel解码失败', e)
        return SnatcherResponse(ResponseCodes.INVALID_TOKEN)
    energy_collection = collections['energy']
    energy = energy_collection.query_one(BSONObjectId(fuel_id))
    data = export_progress(fuel_id, energy['username'])
    return SnatcherResponse(ResponseCodes.OK, data)


@router.get('/selection', summary='查询课程已选择人数')
async def query_course_selected(course_type: CourseTypeEnum):
    async with AIORedis(**settings.DATABASES['redis']['public'], decode_responses=True) as conn:
        data = await conn.hgetall(course_type.value + '_course_stock')
    return SnatcherResponse(ResponseCodes.OK, data)
