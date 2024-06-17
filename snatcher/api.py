"""
Some interfaces of this project to start.
    1. The `physical_education` function:
        A interface to send a 'PE' select course task to celery task queue.

    2. The `public_choice` function:
        A interface to send a 'PC' select course task to celery task queue.

    3. The `async_physical_education` coroutine function:
        A asynchronous interface to send a 'PE' select course task to aio-celery task queue.

    4. The `async_public_choice` coroutine function:
        A asynchronous interface to send a 'PC' select course task to aio-celery task queue.

For all functions parameters:
    1. goals: [(course_name, course_id),...]
    2. users: It must contain: username, password, email, verify_code
"""
# from snatcher.tasks import select_course
from snatcher.aiotasks import async_select_course, application


# def physical_education(
#     goals: list[tuple[str, str]],
#     **users
# ):
#     select_course.delay(goals, 'PE', **users)
#
#
# def public_choice(
#     goals: list[tuple[str, str]],
#     **users
# ):
#     select_course.delay(goals, 'PC', **users)


async def async_physical_education(
    goals: list[tuple[str, str]],
    **users
):
    async with application.setup():
        await async_select_course.delay(goals, 'PE', **users)


async def async_public_choice(
    goals: list[tuple[str, str]],
    **users
):
    async with application.setup():
        await async_select_course.delay(goals, 'PC', **users)
