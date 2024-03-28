"""
Some interfaces of this project to start.
    1. The `physical_education` function:
        A interface to send a 'PE' select course task to celery task queue.

    2. The `public_choice` function:
        A interface to send a 'PC' select course task to celery task queue.
"""
from .tasks import select_course


def physical_education(
    goals: list[tuple[str, str]],
    **users
):
    """
    send a PE select course task.
    :param goals: [(course_name, course_id),...]
    :param users: It must contain: username, password, email, verify_code
    :return:
    """
    select_course.delay(goals, 'PE', **users)


def public_choice(
    goals: list[tuple[str, str]],
    **users
):
    """
    send a PC select course task.
    :param goals: [(course_name, course_id),...]
    :param users: It must contain: username, password, email, verify_code
    :return:
    """
    select_course.delay(goals, 'PC', **users)
