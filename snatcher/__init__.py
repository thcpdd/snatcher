"""
The snatcher package information:
    1. `storage` package:
        Providing some way to control MySQL and Redis database.
    2. `selector` package:
        Some course selectors in this package, which are used for course selection.
    3. `api` module:
        Providing some interfaces for outer caller.
    4. `conf` module:
        Some configurations of snatcher.
    5. `postman` package:
        Wrapping a shortcuts for sending email.
    6. `session` module:
        Some ways to control user's session.
    7. `tasks` module(It was abandoned in 2024-6-17):
        Some configurations and function about celery.
    8. `aiotasks` module:
        An async celery task queue.
    9. `utils` module:
        Some tools in this module.

Usage:
    from snatcher import async_physical_education

    if it was used in the async function inner:
        await async_physical_education(
            [(course_name, course_id), ...],
            username='your_username',
            password='your_password',
            email='rainbow59216@rainbow.com',
            verify_code='your_verify_code'
        )

    if it was used in outer:
        import asyncio

        asyncio.run(async_physical_education(
            [(course_name, course_id), ...],
            username='your_username',
            password='your_password',
            email='rainbow59216@rainbow.com',
            verify_code='your_verify_code'
        ))
"""
# from .api import (
#     async_public_choice as async_public_choice,
#     async_physical_education as async_physical_education
# )
