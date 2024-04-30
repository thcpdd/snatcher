"""
Course selector performers here:
    All course selector will be proxy call by performer.
"""
from snatcher.db.mysql import vc_querier
from snatcher.mail import send_email
from .sync_selector import SynchronousCourseSelector
from .async_selector import AsynchronousCourseSelector


def selector_performer(
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]],
    selector: SynchronousCourseSelector,
):
    for course_name, course_id in goals:
        selector.update_selector_info(course_name, course_id, email)
        result = selector.select()
        if result == 1:
            vc_querier.update(selector.username, verify_code)
            success, exception = send_email(email, selector.username, course_name)
            if not success:
                selector.log.set_others('send_email_failed', str(exception))
            break


async def async_selector_performer(
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]],
    selector: AsynchronousCourseSelector,
):
    for course_name, course_id in goals:
        selector.update_selector_info(course_name, course_id, email)
        result = await selector.select()
        if result == 1:
            vc_querier.update(selector.username, verify_code)
            success, exception = send_email(email, selector.username, course_name)
            if not success:
                selector.log.set_others('send_email_failed', str(exception))
            break
