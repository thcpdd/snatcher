"""
The module of celery configuration and its task function:
    You can launch a celery worker usage:
        celery -A snatcher.tasks worker -l INFO -P eventlet --concurrency=12

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

from snatcher.conf import settings
from snatcher.session import check_and_set_session
from snatcher.selector.sync_selector import (
    SynchronousPhysicalEducationCourseSelector as PESelector,
    SynchronousPublicChoiceCourseSelector as PCSelector,
)
from snatcher.selector.performers import selector_performer
from snatcher.db.mysql import fd_querier


backend = 'redis://127.0.0.1:6379/1'
broker = 'redis://127.0.0.1:6379/2'

application = Celery('snatcher', backend=backend, broker=broker, broker_connection_retry_on_startup=True)


@application.task(name='snatcher.tasks.physical_education_task')
def physical_education_task(
    username: str,
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]]
):
    selector_performer(email, verify_code, goals, PESelector(username))


@application.task(name='snatcher.tasks.public_choice_task')
def public_choice_task(
    username: str,
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]]
):
    selector_performer(email, verify_code, goals, PCSelector(username))


tasks = {
    'PC': public_choice_task,
    'PE': physical_education_task
}


@application.task(name='snatcher.tasks.select_course')
def select_course(
    goals: list[tuple[str, str]],
    course_type: str,
    **users
):
    task: Task | None = tasks.get(course_type)
    username = users.get('username')
    if task is None:
        fd_querier.insert(username, '', '', '选择了不支持的课程类型', 0)
        return
    password = users.get('password')
    result = check_and_set_session(username, password)
    if result == -1:
        return
    start_time = settings.start_time()
    email = users.get('email')
    verify_code = users.get('verify_code')
    task.apply_async(eta=start_time, args=(username, email, verify_code, goals))
