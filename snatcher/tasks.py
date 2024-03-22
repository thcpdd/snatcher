"""
The module of celery configuration and its task function:
    You can launch a celery worker usage:
        1. celery -A snatcher.tasks worker -l INFO --pool=threads --concurrency=12
        2. celery -A snatcher.tasks worker -l INFO -P eventlet --concurrency=12

    1. The `application` object:
        It is a celery instance.

    2. The `physical_education_task` task.
        It will send a 'PE' task to celery task queue.

    3. The `public_choice_task` task.
        It will send a 'PC' task to celery task queue.

    4. The `select_course` task:
        Providing an interface for outer caller.
"""
from celery import Celery, Task

from .conf import settings
from .session import check_and_set_session
from .selector.sync_selector import (
    SynchronousPhysicalEducationCourseSelector,
    SynchronousPublicChoiceCourseSelector,
)
from .selector.base import selector_performer
from .db.mysql import create_failed_data


backend = 'redis://127.0.0.1:6379/1'
broker = 'redis://127.0.0.1:6379/2'

application = Celery('snatcher', backend=backend, broker=broker)


@application.task(name='snatcher.tasks.physical_education_task')
def physical_education_task(
    username: str,
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]]
):
    selector_performer(email, verify_code, goals, SynchronousPhysicalEducationCourseSelector(username))


@application.task(name='snatcher.tasks.public_choice_task')
def public_choice_task(
    username: str,
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]]
):
    selector_performer(email, verify_code, goals, SynchronousPublicChoiceCourseSelector(username))


@application.task(name='snatcher.tasks.select_course')
def select_course(
    goals: list[tuple[str, str]],
    course_type: str,
    **users
):
    tasks = {
        'PC': public_choice_task,
        'PE': physical_education_task
    }
    task: Task | None = tasks.get(course_type)
    username, password, email = users.get('username'), users.get('password'), users.get('email')
    if task is None:
        create_failed_data(username, '', '', '选择了不支持的课程类型', 0)
        return
    result = check_and_set_session(username, password)
    if result == -1:
        return
    start_time = settings.start_time()
    task.apply_async(eta=start_time, args=(username, email, users.get('verify_code'), goals))
