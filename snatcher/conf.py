"""
The project settings.

Usage:
    from snatcher.conf import settings
"""
from datetime import datetime, timezone
from functools import lru_cache

from arq.connections import RedisSettings


class SingletonMetaClass(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            _instance = super().__call__(*args, **kwargs)
            setattr(cls, '_instance', _instance)
        else:
            _instance = getattr(cls, '_instance')
        return _instance


class Settings(metaclass=SingletonMetaClass):
    # Is it a development environment.
    DEVELOPMENT_ENVIRONMENT = True

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
            'public': {
                'db': 5,
                'host': '127.0.0.1'
            }
        },
        'mongodb': {
            'uri': ''
        }
    }

    # Global request timeout(except at setting session), unit is second.
    TIMEOUT: int = 60 * 60 * 2

    # It was used in setting session timeout, unit is second.
    SETTING_SESSION_TIMEOUT: int = 60 * 60

    # Study term.
    # Last term is 3, next term is 12.
    TERM: int = 3

    # study year
    SELECT_COURSE_YEAR: int = 2024

    # Study term period.
    # The first half of the term is 1, the second half of the term is 2.
    PERIOD: int = 2

    # Selecting course start time.
    START_TIME: dict = {
        'year': 2024,
        'month': 6,
        'day': 29,
        'hour': 9,
        'minute': 0,
        'second': 1
    }

    # The email configurations.
    EMAIL_CONFIG: dict = {
        'sender': 'rainbow59216@foxmail.com',
        'name': '智能抢课系统-邮箱小助手',
        'password': 'updgvszsuymydajg',
        'host': 'smtp.qq.com',
        'port': 465
    }

    # Value is True:
    #   Sending email by 'tencent cloud service' when select course successful.
    # Value is False:
    #   Sending email by 'SMTP' when select course successful.
    USE_TENCENT_CLOUD_MAIL_SERVICE = True

    # All request ports(host number).
    PORTS: list[str] = ['5', '6', '7', '8', '9']

    # It determines the time for booking courses.
    SYSTEM_OPENING_TIME: dict = {
        'pc': {
            'year': 2049,
            'month': 10,
            'day': 1,
            'hour': 15,
            'minute': 0,
            'second': 0
        },
        'pe': {
            'year': 2049,
            'month': 10,
            'day': 1,
            'hour': 15,
            'minute': 0,
            'second': 0
        }
    }

    # Task queue redis settings.
    ARQ_REDIS_SETTINGS = RedisSettings(host='127.0.0.1', database=1)

    @lru_cache()
    def start_time(self) -> datetime:
        """The `START_TIME` convert to datatime object."""
        return datetime.fromtimestamp(datetime(**self.START_TIME).timestamp(), timezone.utc)

    @lru_cache()
    def system_opening_time(self, course_type: str) -> datetime:
        opening_time = self.SYSTEM_OPENING_TIME.get(course_type)
        if opening_time is None:
            return datetime(year=2049, month=10, day=1, hour=15)
        return datetime(**opening_time)

    def countdown(self) -> int:
        """The countdown time of start time."""
        if self.start_time() <= datetime.now(timezone.utc):
            return 0
        return (self.start_time() - datetime.now(timezone.utc)).seconds

    def get_mongodb_uri(self) -> str:
        if not (mongodb_uri := self.DATABASES['mongodb']['uri']):
            if self.DEVELOPMENT_ENVIRONMENT:
                mongodb_config_file = 'mongodb_dev'
            else:
                mongodb_config_file = 'mongodb'
            with open(mongodb_config_file) as f:
                mongodb_uri = f.read().strip()
            self.DATABASES['mongodb']['uri'] = mongodb_uri
        return mongodb_uri


settings = Settings()
