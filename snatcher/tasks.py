"""
celery -A snatcher.tasks worker -l INFO --pool=threads --concurrency=12
celery -A snatcher.tasks worker -l INFO -P eventlet --concurrency=12
celery -A snatcher.tasks worker -l INFO -P gevent --concurrency=12
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
    """
    选课成功结果通知
    :param receiver_email:
    :param username:
    :param course_name:
    :return:
    """
    subject = '选课结果通知'
    content = '学号为%s的同学：\n你好，您意向的课程《%s》已经选课成功，感谢您对我们的信任，谢谢！' % (username, course_name)
    send_mail(receiver_email, subject, content)


def task_caller(
    conditions: list,
    username: str,
    email: str,
    selector: CourseSelector
):
    """
    任务调用者
    :param conditions: 过滤条件
    :param username: 用户名
    :param email: 邮箱
    :param selector: 选择器
    :return:
    """
    for condition in conditions:
        selector.update_filter_condition(condition)
        result = selector.select()
        create_selected_data(username, email, selector.real_name, selector.log.key)
        if result == 1:
            send_email.apply_async(args=(email, username, selector.real_name))
            break


@application.task(name='snatcher.tasks.physical_education_task')
def physical_education_task(conditions: list, username: str, email: str):
    """体育课选课任务"""
    task_caller(conditions, username, email, SynchronousPhysicalEducationCourseSelector(username))


@application.task(name='snatcher.tasks.public_choice_task')
def public_choice_task(conditions: list, username: str, email: str):
    """公选课选课任务"""
    task_caller(conditions, username, email, SynchronousPublicChoiceCourseSelector(username))


@application.task(name='snatcher.tasks.snatcher')
def select_course(
    username: str,
    password: str,
    conditions: list,
    course_type: str,
    email: str
):
    """
    选课接口
    :param username: 学号
    :param password: 密码
    :param conditions: 所有过滤条件 ['珍珠球', '排球']
    :param course_type: 课程类型，公选课 'PC'、英语课 'EG'、体育课 'PE'
    :param email: 邮箱
    :return:
    """
    tasks = {
        'PC': public_choice_task,
        'PE': physical_education_task
    }
    task = tasks.get(course_type)
    if not task:
        create_failed_data(username, '', '', '选择了不支持的课程类型')
        return
    result = check_and_set_session(username, password)
    if result == -1:
        return
    start_time = datetime.utcfromtimestamp(datetime(**settings.START_TIME).timestamp())
    task.apply_async(eta=start_time, args=(conditions, username, email))
