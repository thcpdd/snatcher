"""
Course selector performers here:
    All course selector will be proxy call by performer.
"""
from snatcher.db.mysql import vc_querier, scd_querier
from snatcher.db.cache import remove_code_is_using
from snatcher.postman.mail import send_email
# from .sync_selector import SynchronousCourseSelector
from .async_selector import AsynchronousCourseSelector


# def selector_performer(
#     email: str,
#     verify_code: str,
#     goals: list[tuple[str, str]],
#     selector: SynchronousCourseSelector,
# ):
#     for course_name, course_id in goals:
#         selector.update_selector_info(course_name, course_id, email)
#         result = selector.select()
#         if result == 1:
#             vc_querier.update(selector.username, verify_code)
#             success, exception = send_email(email, selector.username, course_name)
#             if not success:
#                 selector.log.set_others('send_email_failed', exception)
#             break


async def async_selector_performer(
    selector_class: type[AsynchronousCourseSelector],
    username: str,
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]],
):
    """Proxying call and perform the course_selector."""
    selector = selector_class(username)
    for course_name, course_id in goals:
        selector.update_selector_info(course_name, course_id, email)
        result = await selector.select()
        if result == 1:
            vc_querier.update(selector.username, verify_code)
            scd_querier.mark_success(selector.latest_selected_data_id)
            success, exception = send_email(email, username, course_name)
            if not success:
                selector.log.set_others('send_email_failed', exception)
            break
    remove_code_is_using(verify_code)
