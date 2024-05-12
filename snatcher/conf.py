"""
The project settings.
"""
from datetime import datetime, timezone


class SingletonMetaClass(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            _instance = super().__call__(*args, **kwargs)
            setattr(cls, '_instance', _instance)
        return getattr(cls, '_instance')


class Settings(metaclass=SingletonMetaClass):
    # Database configurations.
    DATABASES: dict = {
        'redis': {
            'log': {
                'db': 3,
                'host': '127.0.0.1'
            },
            'session': {
                'db': 4,
                'host': '127.0.0.1'
            },
            'weights': {
                'db': 5,
                'host': '127.0.0.1'
            }
        },
        'mysql': {
            'database': 'snatcher',
            'host': '127.0.0.1',
            'user': 'root',
            'password': '000000',
            'port': 3306,
        }
    }

    # Global request timeout(except at setting session), unit is second.
    TIMEOUT: int = 60 * 60

    # It was used in setting session timeout, unit is second.
    SETTING_SESSION_TIMEOUT: int = 60 * 30

    # Study term.
    # Last term is 3, next term is 12.
    TERM: int = 12

    # study year
    SELECT_COURSE_YEAR: int = 2023

    # Study term period.
    # The first half of the term is 1, the second half of the term is 2.
    PERIOD: int = 2

    # Selecting course start time.
    START_TIME: dict = {
        'year': 2024,
        'month': 4,
        'day': 22,
        'hour': 12,
        'minute': 30,
        'second': 1
    }

    # The email configurations.
    EMAIL_CONFIG: dict = {
        'email_from': 'rainbow59216@foxmail.com',  # your email address
        'name': '智能抢课系统-邮箱小助手',  # your name
        'verify_code': 'egpzpjrwjhzsdcbb',  # your email verify code
        'host': 'smtp.qq.com',  # current email host
        'port': 465  # current email port
    }

    # All request ports(host number).
    PORTS: list[str] = ['5', '6', '7', '8', '9']

    def start_time(self) -> datetime:
        """The `START_TIME` convert to datatime object."""
        return datetime.fromtimestamp(datetime(**self.START_TIME).timestamp(), timezone.utc)

    def countdown(self) -> int:
        """The countdown time of start time."""
        if self.start_time() <= datetime.now(timezone.utc):
            return 0
        return (self.start_time() - datetime.now(timezone.utc)).seconds


settings = Settings()
