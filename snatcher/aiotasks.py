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
import time

from aio_celery import Celery
from aio_celery.annotated_task import AnnotatedTask

from snatcher.conf import settings
from snatcher.selector.async_selector import (
    AsynchronousPublicChoiceCourseSelector as AsyncPCSelector,
    AsynchronousPhysicalEducationCourseSelector as AsyncPESelector
)
from snatcher.storage.mongo import collections, get_security_key, decrypt_fuel, BSONObjectId, update_fuel_status
from snatcher.selector.performers import async_selector_performer
from snatcher.postman.mail import send_email
from snatcher.session import async_check_and_set_session


application = Celery('snatcher')
application.conf.result_backend = 'redis://127.0.0.1:6379/1'


@application.task(
    name='pe_task',
    autoretry_for=(Exception,),
    max_retries=2,
    default_retry_delay=5
)
async def async_physical_education_task(
    username: str,
    email: str,
    fuel_id: str,
    goals: list[tuple[str, str]]
):
    await async_selector_performer(AsyncPESelector, username, email, fuel_id, goals)


@application.task(
    name='pc_task',
    autoretry_for=(Exception,),
    max_retries=2,
    default_retry_delay=5
)
async def async_public_choice_task(
    username: str,
    email: str,
    fuel_id: str,
    goals: list[tuple[str, str]]
):
    await async_selector_performer(AsyncPCSelector, username, email, fuel_id, goals)


@application.task(name='select_course')
async def async_select_course(
    goals: list[tuple[str, str]],
    course_type: str,
    **users
):
    task: AnnotatedTask | None

    match course_type:  # The version of Python >= 3.10
        case 'PC':
            task = async_public_choice_task
        case 'PE':
            task = async_physical_education_task
        case _:
            task = None

    username = users.get('username')

    failure_collection = collections['failure']

    if task is None:
        failure_collection.create(username, '', '', 0, '选择了不支持的课程类型')
        return

    fuel = users.get('fuel')
    key = get_security_key('fuel')
    fuel_id = decrypt_fuel(fuel, key)
    update_fuel_status(BSONObjectId(fuel_id), 'using')

    password = users.get('password')

    result = await async_check_and_set_session(username, password)
    if result == -1:
        failure_collection.create(username, '', '', 0, '模拟登录失败')
        send_email('1834763300@qq.com', username, '', False, '模拟登录失败')
        update_fuel_status(BSONObjectId(fuel_id), status='unused')
        return

    countdown = settings.countdown()
    email = users.get('email')

    await task.apply_async(
        args=(username, email, fuel_id, goals),
        countdown=countdown,
        task_id=f'{username}-{int(time.time())}'
    )
