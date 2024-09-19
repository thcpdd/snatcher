"""
Asyncio Celery Tasks:
    You can launch an async celery worker usage:
        aio_celery worker snatcher.aiotasks:application --concurrency=12

    1. The `application` object:
        It is an async celery instance.

    2. The `async_physical_education_task` task.
        It will send a 'PE' async task to async celery task queue.

    3. The `async_public_choice_task` task.
        It will send a 'PC' async task to async celery task queue.

    4. The `async_select_course` task:
        Providing an interface for outer caller.
"""
import traceback
import asyncio
import time

import aiohttp
from aiohttp.client_exceptions import ContentTypeError
from redis.asyncio import Redis as AIORedis
from arq import ArqRedis, Retry

from snatcher.conf import settings
from snatcher.selector.async_selector import (
    AsynchronousPublicChoiceCourseSelector as AsyncPCSelector,
)
from snatcher.storage.mongo import collections, get_security_key, decrypt_fuel, BSONObjectId, update_fuel_status
from snatcher.selector.performers import async_selector_performer
from snatcher.postman.mail import send_email
from snatcher.session import async_check_and_set_session, get_session_manager


async def public_choice_task(
    _: dict,
    username: str,
    email: str,
    fuel_id: str,
    goals: list[tuple[str, str, str]]
):
    try:
        await async_selector_performer(AsyncPCSelector, username, email, fuel_id, goals)
    except Exception:
        print('Unexpected error during selecting course. Detail stack information:')
        traceback.print_exc()
        update_fuel_status(BSONObjectId(fuel_id), 'unused')
        raise Retry(5)


async def select_course(
    context: dict,
    goals: list[tuple[str, str, str]],
    **users
):
    username = users.get('username')

    failure_collection = collections['failure']

    fuel = users.get('fuel')
    key = get_security_key('fuel')
    fuel_id = decrypt_fuel(fuel, key)
    update_fuel_status(BSONObjectId(fuel_id), 'using')

    password = users.get('password')

    if password:
        result = await async_check_and_set_session(username, password)
        if result == -1:
            failure_collection.create(username, '', '', 0, '模拟登录失败')
            send_email('1834763300@qq.com', username, '', success=False, failed_reason='模拟登录失败')
            update_fuel_status(BSONObjectId(fuel_id), status='unused')
            return
    else:
        cookie, port = users.get('cookie'), users.get('port')
        session_manager = get_session_manager(username)
        if not session_manager.has_session(port):
            session_manager.save_cookie(cookie, port)

    countdown = settings.countdown()
    email = users.get('email')

    arq_redis: ArqRedis = context['redis']
    await arq_redis.enqueue_job(
        'public_choice_task',
        username,
        email,
        fuel_id,
        goals,
        _job_id=f'{username}-{int(time.time())}',
        _defer_by=countdown
    )


async def query_selected_number_task(
    _: dict,
    course_type: str,
    username: str,
    cookie: str,
    port: str,
    frequency: int = 5
):
    url = 'http://10.3.132.%s/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512' % port
    cookies = {'JSESSIONID': cookie}
    data = {
        'bklx_id': 0,
        'xkxnm': settings.SELECT_COURSE_YEAR,
        'xkxqm': settings.TERM,
        'kklxdm': course_type,
        'kspage': 1,
        'jspage': 500,
    }
    if course_type == '05':
        data.update({
            'njdm_id': '20' + username[:2],
            'zyfx_id': '666',
            'bh_id': '666',
            'xbm': '666',
            'xslbdm': '666',
            'mzm': '666',
            'xz': '666',
            'ccdm': '666',
            'xsbj': '666',
            'xqh_id': '666',
            'jg_id': '206',
        })

    name = course_type + '_course_stock'
    stop_sign = course_type + '_stop'
    timeout = aiohttp.ClientTimeout(settings.TIMEOUT)

    async with AIORedis(**settings.DATABASES['redis']['public'], decode_responses=True) as conn:
        stop = await conn.get(stop_sign)
        if stop:
            await conn.delete(stop_sign)
        async with aiohttp.ClientSession(cookies=cookies, timeout=timeout) as session:
            while True:
                stop = await conn.get(stop_sign)
                if stop and stop == '1':
                    break

                try:
                    response = await session.post(url, data=data)
                except Exception as exception:
                    print('query_selected_number异常退出1', exception)
                    break

                try:
                    courses = await response.json()
                except ContentTypeError as exception:
                    print('query_selected_number异常退出2', exception)
                    break

                for course in courses['tmpList']:
                    await conn.hset(name, course['jxb_id'], course['yxzrs'])
                await conn.hset(name, 'updated_at', str(time.time()))

                await asyncio.sleep(60 * frequency)


class WorkerSettings:
    """
    取消任务完成时的保存：注释 arq.worker 第 696 行
    取消任务失败时的保存：注释 arq.worker 第 719 行
    """
    functions = [public_choice_task, select_course, query_selected_number_task]
    redis_settings = settings.ARQ_REDIS_SETTINGS
    max_jobs = 1000
    job_timeout = 60 * 60 * 2
    allow_abort_jobs = True
    max_tries = 3
