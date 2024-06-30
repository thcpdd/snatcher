"""
Some operations of redis here:
    1. The `PortWeightManager` class:
        Managing every port weight.

    2. The `RunningLogs` class:
        Recoding the log during running.
        -- `set` method:
            Setting a value from instance messages.
            The name must be in ['step-1_kch_id', 'step-3_jxb_ids', 'step-2_xkkz_id'].
        -- `set_others` method:
            It just like `hset`.
        -- `retry` method:
            Add retry count when the task was failing.
        -- `timeout` method:
            Add timeout count when the task was timeout.

    3. The `AsyncRunningLogs` class:
        An async running logs class. All operations by `redis.asyncio.Redis`.
        You need mind the help document of this class.
"""
from redis import Redis
from redis.asyncio import Redis as AIORedis

from snatcher.conf import settings


# WEIGHTS_NAME = 'weights'
USING_CODES_NAME = 'using-codes'
CHANNEL_NAME = 'logs-change'


# Creating a global variable for controlling the public cache.
public_cache = Redis(**settings.DATABASES['redis']['public'], decode_responses=True)


# --------------------------------------------- #
# Some functions for controlling port's weight. #
# --------------------------------------------- #
# def optimal_port_generator():
#     def get_optimal_port():
#         rank = 0
#
#         def inner() -> list:
#             nonlocal rank
#
#             _port_list = public_cache.zrange(WEIGHTS_NAME, rank, rank)
#             rank += 1
#             return _port_list
#         return inner
#
#     optimal_port = get_optimal_port()
#     while port_list := optimal_port():
#         yield port_list[0]
#
#
# def decreasing_weight(port: str, decrease_size: int | float = 20):
#     weight = public_cache.zscore(WEIGHTS_NAME, port)
#     public_cache.zadd(WEIGHTS_NAME, {port: weight - decrease_size})
#
#
# def increasing_weight(port: str, increase_size: int | float = 10):
#     weight = public_cache.zscore(WEIGHTS_NAME, port)
#     public_cache.zadd(WEIGHTS_NAME, {port: weight + increase_size})
#
#
# def add_using_number(port: str, num: int | float = None):
#     if num is None:
#         weight = public_cache.zscore(WEIGHTS_NAME, port) + 1
#     else:
#         weight = num
#     public_cache.zadd(WEIGHTS_NAME, {port: weight})
#
#
# def reduce_using_number(port: str):
#     weight = public_cache.zscore(WEIGHTS_NAME, port)
#     public_cache.zadd(WEIGHTS_NAME, {port: weight - 1})


# ------------------------------------------------ #
# Some functions for controlling all verify codes. #
# ------------------------------------------------ #
def mark_code_is_using(verify_code: str):
    public_cache.sadd(USING_CODES_NAME, verify_code)


def remove_code_is_using(verify_code: str):
    public_cache.srem(USING_CODES_NAME, verify_code)


def judge_code_is_using(verify_code: str) -> int:
    """if 1 is using, else not using"""
    return public_cache.sismember(USING_CODES_NAME, verify_code)


# -------------------------------------------------------------- #
# Some functions for achieving to publish messages into channel. #
# -------------------------------------------------------------- #
def publish_message(func):
    """
    Publishing a message into `logs-shift` channel.

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
    key, name, msg = message.split('|')
    username, course_name = key.split('-')
    return {
        'username': username,
        'course_name': course_name,
        'name': name,
        'msg': msg
    }


# --------------------------------------------------------- #
# Some functions or classes for controlling running logger. #
# --------------------------------------------------------- #
class AsyncRuntimeLogger:
    """
    You must call `close` method before function was garbage collected.

    Example:
         (Recommendation) Using it as a context manager in the coroutine function:
            async def test():
                async with AsyncRunningLogs('your_key') as logs:
                    ...  # your operations

        You can also use it by creating object, but don't forget to call `close` method:
            async def test():
                logs = AsyncRunningLogs('your_key')
                ...  # your operations
                await logs.close()  # It is must !!!
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
