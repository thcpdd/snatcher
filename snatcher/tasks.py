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
from datetime import datetime

from celery import Celery

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
def physical_education_task(conditions: list, username: str, email: str):
    selector_performer(conditions, username, email, SynchronousPhysicalEducationCourseSelector(username))


@application.task(name='snatcher.tasks.public_choice_task')
def public_choice_task(conditions: list, username: str, email: str):
    selector_performer(conditions, username, email, SynchronousPublicChoiceCourseSelector(username))


@application.task(name='snatcher.tasks.select_course')
def select_course(
    username: str,
    password: str,
    conditions: list[str],
    course_type: str,
    email: str
):
    tasks = {
        'PC': public_choice_task,
        'PE': physical_education_task
    }
    task = tasks.get(course_type)
    if not task:
        create_failed_data(username, '', '', '选择了不支持的课程类型', 0)
        return
    result = check_and_set_session(username, password)
    if result == -1:
        return
    start_time = datetime.utcfromtimestamp(datetime(**settings.START_TIME).timestamp())
    task.apply_async(eta=start_time, args=(conditions, username, email))
