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
from snatcher.selector.performers import async_selector_performer
from snatcher.db.mysql import fd_querier
from snatcher.db.cache import mark_code_is_using
from snatcher.session import async_check_and_set_session


application = Celery('snatcher')
application.conf.result_backend = 'redis://127.0.0.1:6379/1'


@application.task(
    name='snatcher.aiotasks.async_physical_education_task',
    autoretry_for=(Exception,),
    max_retries=2,
    default_retry_delay=5
)
async def async_physical_education_task(
    username: str,
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]]
):
    await async_selector_performer(AsyncPESelector, username, email, verify_code, goals)


@application.task(
    name='snatcher.aiotasks.async_public_choice_task',
    autoretry_for=(Exception,),
    max_retries=2,
    default_retry_delay=5
)
async def async_public_choice_task(
    username: str,
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]]
):
    await async_selector_performer(AsyncPCSelector, username, email, verify_code, goals)


aiotasks = {
    'PC': async_public_choice_task,
    'PE': async_physical_education_task
}


@application.task(name='snatcher.aiotasks.async_select_course')
async def async_select_course(
    goals: list[tuple[str, str]],
    course_type: str,
    **users
):
    task: AnnotatedTask | None = aiotasks.get(course_type)
    username = users.get('username')
    if task is None:
        fd_querier.insert(username, '', '', '选择了不支持的课程类型', 0)
        return
    verify_code = users.get('verify_code')
    mark_code_is_using(verify_code)
    password = users.get('password')
    result = await async_check_and_set_session(username, password)
    if result == -1:
        return
    countdown = settings.countdown()
    email = users.get('email')
    await task.apply_async(
        args=(username, email, verify_code, goals),
        countdown=countdown,
        task_id=f'{username}-{int(time.time())}'
    )
