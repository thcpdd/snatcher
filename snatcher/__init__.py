"""
The snatcher package information:
    1. `db` package:
        Providing some way to control mysql database.
    2. `selector` package:
        Some selectors in this package.
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

Usage:
    from snatcher import physical_education  # the PE interface.
    from snatcher import public_choice  # the PC interface.

    physical_education(your_username, your_password, ['goal1', ...], 'rainbow59216@rainbow.com')
"""
from .api import (
    physical_education as physical_education,
    public_choice as public_choice,
)
