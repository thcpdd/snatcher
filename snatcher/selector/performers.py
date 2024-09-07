"""
Course selector performers here:
    All course selector will be proxy call by performer.
"""
from snatcher.storage.mongo import collections, BSONObjectId, update_fuel_status
from snatcher.postman.mail import send_email
from .async_selector import AsynchronousCourseSelector


async def async_selector_performer(
    selector_class: type[AsynchronousCourseSelector],
    username: str,
    email: str,
    fuel_id: str,
    goals: list[tuple[str, str]],
):
    """Proxying call and perform the course_selector."""
    submitted_collection = collections['submitted']
    failure_collection = collections['failure']

    async with selector_class(username, fuel_id) as selector:
        fuel_id = BSONObjectId(fuel_id)

        for course_name, course_id in goals:
            log_key = username + '-' + course_name
            row_id = submitted_collection.create(
                username=username,
                email=email,
                course_name=course_name,
                log_key=log_key
            )
            await selector.update_selector_info(course_name, course_id, log_key)

            code, message = await selector.select()

            if code == 1:
                update_fuel_status(fuel_id, status='used')
                submitted_collection.update(row_id, success=1)
                success, exception = send_email(email, username, course_name)
                if not success:
                    print(f'邮件发送失败：{username}-{course_name}', exception)
                break

            failure_collection.create(
                username=username,
                course_name=course_name,
                log_key=log_key,
                reason=message,
                port=int(selector.port)
            )
            send_email('1834763300@qq.com', username, course_name, False, message)
        else:
            update_fuel_status(fuel_id, status='unused')
