import binascii

from fastapi import APIRouter, Path

from .validators import PCValidator, PEValidator, BookPEValidator, BookPCValidator
from backend.response import SnatcherResponse, ResponseCodes
from snatcher import async_public_choice, async_physical_education
from snatcher.storage.mongo import get_fuel_status, collections


router = APIRouter(prefix='/vpn', tags=['VPN'])


def check_fuel(username: str, fuel: str) -> tuple[int, str]:
    try:
        status = get_fuel_status(username, fuel)
    except binascii.Error:
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
