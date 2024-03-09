"""
The module of celery configuration and its task function:
    You can launch a celery worker usage:
        1. celery -A snatcher.tasks worker -l INFO --pool=threads --concurrency=12
        2. celery -A snatcher.tasks worker -l INFO -P eventlet --concurrency=12

    1. The `application` object:
        It is a celery instance.

    2. The `send_email` task:
        It is a celery task function. It will send an email into appoint user.

    3. The `selector_caller` function:
        It will perform relevant logic for a selector instance.

    4. The `physical_education_task` task.
        It will send a 'PE' task to celery task queue.

    5. The `public_choice_task` task.
        It will send a 'PC' task to celery task queue.

    6. The `select_course` task:
        Providing an interface for outer caller.
        Detail call way to see if __name__ == '__main__'.
"""
from datetime import datetime

from celery import Celery

from .conf import settings
from .mail import send_email as send_mail
from .session import (
    check_and_set_session
)
from .selector.sync_selector import (
    SynchronousPhysicalEducationCourseSelector,
    SynchronousPublicChoiceCourseSelector,
    CourseSelector
)
from .db.mysql import (
    create_selected_data,
    create_failed_data
)


backend = 'redis://127.0.0.1:6379/1'
broker = 'redis://127.0.0.1:6379/2'

application = Celery('snatcher', backend=backend, broker=broker)


@application.task(name='snatcher.tasks.send_email')
def send_email(receiver_email: str, username: str, course_name: str):
    subject = '选课结果通知'
    content = '学号为%s的同学：\n你好，您意向的课程《%s》已经选课成功，感谢您对我们的信任，谢谢！' % (username, course_name)
    send_mail(receiver_email, subject, content)


def selector_caller(
    conditions: list,
    username: str,
    email: str,
    selector: CourseSelector
):
    for condition in conditions:
        selector.update_filter_condition(condition)
        result = selector.select()
        create_selected_data(username, email, selector.real_name, selector.log.key)
        if result == 1:
            send_email.apply_async(args=(email, username, selector.real_name))
            break


@application.task(name='snatcher.tasks.physical_education_task')
def physical_education_task(conditions: list, username: str, email: str):
    selector_caller(conditions, username, email, SynchronousPhysicalEducationCourseSelector(username))


@application.task(name='snatcher.tasks.public_choice_task')
def public_choice_task(conditions: list, username: str, email: str):
    selector_caller(conditions, username, email, SynchronousPublicChoiceCourseSelector(username))


@application.task(name='snatcher.tasks.snatcher')
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


if __name__ == '__main__':
    select_course.delay('your_username', 'your_password', ['condition1', 'condition2'], 'PE', 'email')
