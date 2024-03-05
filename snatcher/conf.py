"""
The project settings.
"""


class _SettingsMeta(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            _instance = super().__call__(*args, **kwargs)
            setattr(cls, '_instance', _instance)
        return getattr(cls, '_instance')


class Settings(metaclass=_SettingsMeta):
    # 数据库连接配置
    DATABASES: dict = {
        'redis': {
            'log': {
                'db': 3,
                'host': '127.0.0.1'
            },
            'session': {
                'db': 4,
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

    # 全局请求超时时间
    TIMEOUT: int = 60 * 20

    # 学期设置
    # 上学期 3，下学期 12
    TERM: int = 12

    # 选课学年
    SELECT_COURSE_YEAR: int = 2023

    # 选课开始时间
    START_TIME = {
        'year': 2024,
        'month': 3,
        'day': 5,
        'hour': 12,
        'minute': 30,
        'second': 1
    }

    # 邮箱配置信息
    EMAIL_CONFIG = {
        'email_from': 'rainbow59216@foxmail.com',  # 邮箱用户
        'name': 'Rainbow',
        'verify_code': 'egpzpjrwjhzsdcbb',  # 邮箱验证码
        'host': 'smtp.qq.com',
        'port': 587
    }

    # 所有发送请求的端口
    PORTS = [5, 6, 9]


settings = Settings()
