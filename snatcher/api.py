"""
Some interfaces of this project to start.
    1. The `async_physical_education` coroutine function:
        A asynchronous interface to send a 'PE' select course task to aio-celery task queue.

    2. The `async_public_choice` coroutine function:
        A asynchronous interface to send a 'PC' select course task to aio-celery task queue.

For all functions parameters:
    1. goals: [(course_name, course_id),...]
    2. users: It must contain: username, password, email, verify_code
"""
from snatcher.aiotasks import async_select_course, application


async def async_physical_education(
    goals: list[tuple[str, str, str]],
    **users
):
    async with application.setup():
        await async_select_course.delay(goals, 'PE', **users)


async def async_public_choice(
    goals: list[tuple[str, str, str]],
    **users
):
    async with application.setup():
        await async_select_course.delay(goals, 'PC', **users)
