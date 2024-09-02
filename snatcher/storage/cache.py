"""
Some operations of Redis here.
"""
from redis import Redis
from redis.asyncio import Redis as AIORedis

from snatcher.conf import settings


USING_CODES_NAME = 'using-codes'
CHANNEL_NAME = 'logs-change'


# -------------------------------------------------------------- #
# Some functions for achieving to publish messages into channel. #
# -------------------------------------------------------------- #
def publish_message(func):
    """
    Publishing a message into `logs-change` channel.

    The format of every massage: 'username-course_name|message_name|message'
    :param func: It will be a coroutine after calling it.
    :return:
    """
    async def publish(*args, **kwargs):
        message = await func(*args, **kwargs)  # Getting the last message.
        self: 'AsyncRuntimeLogger' = args[0]
        if message is not None:
            name: str = args[1]
            message = f'{self.key}|{name}|{message}'
        else:
            message = f'{self.key}|{"retry"}|{self.count - 1}'
        await self._connection.publish(CHANNEL_NAME, message)
    return publish


def parse_message(message: str) -> dict:
    """
    Parsing the message to dict type.
    :param message: 'username-course_name|message_name|message'
    :return:
    """
    key, name, msg = message.split('|')
    username, course_name = key.split('-')
    return {
        'username': username,
        'course_name': course_name,
        'name': name,
        'msg': msg
    }


# --------------------------------------------------------- #
# Some functions or classes for controlling runtime logger. #
# --------------------------------------------------------- #
class AsyncRuntimeLogger:
    """
    Writing runtime logs into Redis and publishing message into channel.

    You must call `close` method before function was collected as garbage.

    Example:
         (Recommendation) Using it as a context manager in the coroutine function:
            async def test():
                async with AsyncRuntimeLogger('your_key') as logger:
                    ...  # your operations

        You can also use it by creating object, but don't forget to call `close` method:
            async def test():
                logger = AsyncRuntimeLogger('your_key')
                ...  # your operations
                await logger.close()  # It is must !!!
    """
    def __init__(self, key: str):
        _db_info = settings.DATABASES['redis']['log']
        self._connection = AIORedis(**_db_info)
        self.key = key
        self.count = 1
        self.messages = {
            'step-1': {
                1: '课程ID设置成功',
                0: '课程ID设置失败'
            },
            'step-3': {
                1: '教学班ID设置成功',
                0: '教学班ID设置失败'
            },
            'step-2': {
                1: 'xkkz_id设置成功',
                0: 'xkkz_id设置失败'
            },
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def wrapper(self, name: str):
        return name + '-' + str(self.count)

    @publish_message
    async def set(self, name: str, success: int = None, message: str = '') -> str:
        if success is not None:
            message = self.messages[name][success]
        await self._connection.hset(self.key, self.wrapper(name), message)
        return message

    @publish_message
    async def retry(self):
        _retry = await self._connection.hget(self.key, 'retry')
        if _retry:
            _retry = int(_retry) + 1
        else:
            _retry = 1
        self.count += 1
        await self._connection.hset(self.key, 'retry', str(_retry))

    async def close(self):
        """You must call this before function was garbage collected."""
        await self._connection.aclose()


def runtime_logs_generator():
    """
    Yielding all runtime logs.

    In a log, which may have many similar fields. But it will generate the latest field.
    Such as, a log have two fields: `step-1-1` and `step-1-2`, which will use `step-1-2` field.

    :return: A generator of {
        'course_name': '',
        'username': '',
        'step-1': '',
        'step-2': '',
        'step-3': '',
        'step-4': '',
        'retry': retry_times
    }
    """
    _db_info = settings.DATABASES['redis']['log']
    conn = Redis(**_db_info, decode_responses=True)
    for _key in conn.keys():
        cache_log = conn.hgetall(_key)
        log = {}
        username, course_name = _key.split('-')
        log.setdefault('course_name', course_name)
        log.setdefault('username', username)
        if retry := cache_log.get('retry'):
            log.setdefault('retry', retry)
            cache_log.pop('retry')
        keys = sorted(cache_log.keys(), reverse=True)
        for key in keys:
            k = key.rsplit('-', maxsplit=1)[0]
            if k not in log:
                log.setdefault(k, cache_log[key])
        yield log
    conn.close()
