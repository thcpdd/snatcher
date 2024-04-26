"""
The project settings.
"""
from datetime import datetime


class SingletonMetaClass(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            _instance = super().__call__(*args, **kwargs)
            setattr(cls, '_instance', _instance)
        return getattr(cls, '_instance')


class Settings(metaclass=SingletonMetaClass):
    # database configurations
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

    # global request timeout, unit is second
    TIMEOUT: int = 60 * 60

    # study term
    # last term is 3, next term is 12
    TERM: int = 12

    # study year
    SELECT_COURSE_YEAR: int = 2023

    # study term period
    # The first half of the term is 1, the second half of the term is 2
    PERIOD: int = 2

    # select course beginning time
    START_TIME: dict = {
        'year': 2024,
        'month': 4,
        'day': 22,
        'hour': 12,
        'minute': 30,
        'second': 1
    }

    # the email configurations
    EMAIL_CONFIG: dict = {
        'email_from': 'rainbow59216@foxmail.com',  # your email address
        'name': 'Rainbow',  # your name
        'verify_code': 'egpzpjrwjhzsdcbb',  # your email verify code
        'host': 'smtp.qq.com',  # current email host
        'port': 587  # current email port
    }

    # all request ports
    PORTS: list[str] = ['5', '6', '7', '8', '9']

    def start_time(self):
        return datetime.utcfromtimestamp(datetime(**self.START_TIME).timestamp())

    def countdown(self):
        if self.start_time() <= datetime.utcnow():
            return 0
        return (self.start_time() - datetime.utcnow()).seconds


settings = Settings()
