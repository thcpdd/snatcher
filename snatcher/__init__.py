"""
The snatcher package information:
    1. `db` package:
        Providing some way to control mysql and redis database.
    2. `selector` package:
        Some course selectors in this package.
    3. `api` module:
        Providing some interfaces for outer caller.
    4. `conf` module:
        Some configurations of snatcher.
    5. `mail` module:
        Wrapping a shortcuts for sending email.
    6. `session` module:
        Some ways to control user's session.
    7. `tasks` module:
        Some configurations and function about celery.
    8. `aiotasks` module:
        An async celery task queue.
    9. `utils` module:
        Some tools in this module.
Usage:
    1. sync function:
        from snatcher import physical_education

        physical_education(
            [(course_name, course_id), ...],
            username='your_username',
            password='your_password',
            email='rainbow59216@rainbow.com',
            verify_code='your_verify_code'
        )
    2. async function:
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
from .api import (
    # physical_education as physical_education,
    # public_choice as public_choice,
    async_public_choice as async_public_choice,
    async_physical_education as async_physical_education
)
