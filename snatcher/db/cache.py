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


WEIGHTS_NAME = 'weights'
USING_CODES_NAME = 'using_codes'


class PublicCacheContextManager:
    def __init__(self):
        self.public_cache: Redis | None = None

    def __enter__(self):
        self.public_cache = Redis(**settings.DATABASES['redis']['public'], decode_responses=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.public_cache.close()


def optimal_port_generator():
    def get_optimal_port(self: PublicCacheContextManager):
        rank = 0

        def inner() -> list:
            nonlocal rank

            _port_list = self.public_cache.zrange(WEIGHTS_NAME, rank, rank)
            rank += 1
            return _port_list
        return inner

    with PublicCacheContextManager() as manager:
        optimal_port = get_optimal_port(manager)
        while port_list := optimal_port():
            yield port_list[0]


def decreasing_weight(port: str, decrease_size: int | float = 20):
    with PublicCacheContextManager() as manager:
        weight = manager.public_cache.zscore(WEIGHTS_NAME, port)
        manager.public_cache.zadd(WEIGHTS_NAME, {port: weight - decrease_size})


def increasing_weight(port: str, increase_size: int | float = 10):
    with PublicCacheContextManager() as manager:
        weight = manager.public_cache.zscore(WEIGHTS_NAME, port)
        manager.public_cache.zadd(WEIGHTS_NAME, {port: weight + increase_size})


def add_using_number(port: str, num: int | float = None):
    with PublicCacheContextManager() as manager:
        if num is None:
            weight = manager.public_cache.zscore(WEIGHTS_NAME, port) + 1
        else:
            weight = num
        manager.public_cache.zadd(WEIGHTS_NAME, {port: weight})


def reduce_using_number(port: str):
    with PublicCacheContextManager() as manager:
        weight = manager.public_cache.zscore(WEIGHTS_NAME, port)
        manager.public_cache.zadd(WEIGHTS_NAME, {port: weight - 1})


def mark_code_is_using(verify_code: str):
    with PublicCacheContextManager() as manager:
        manager.public_cache.sadd(USING_CODES_NAME, verify_code)


def remove_code_is_using(verify_code: str):
    with PublicCacheContextManager() as manager:
        manager.public_cache.srem(USING_CODES_NAME, verify_code)


def judge_code_is_using(verify_code: str) -> int:
    """if 1 is using, else not using"""
    with PublicCacheContextManager() as manager:
        return manager.public_cache.sismember(USING_CODES_NAME, verify_code)


# class RunningLogs:
#     def __init__(self, key: str):
#         _db_info = settings.DATABASES['redis']['log']
#         self._connection = Redis(**_db_info)
#         self.key = key
#         self.messages = {
#             'step-1_kch_id': {
#                 1: '课程ID设置成功',
#                 0: '课程ID设置失败'
#             },
#             'step-3_jxb_ids': {
#                 1: '教学班ID设置成功',
#                 0: '教学班ID设置失败'
#             },
#             'step-2_xkkz_id': {
#                 1: 'xkkz_id设置成功',
#                 0: 'xkkz_id设置失败'
#             },
#         }
#
#     def set(self, name: str, success: int):
#         self._connection.hset(self.key, name, self.messages[name][success])
#
#     def set_others(self, name: str, message: str):
#         self._connection.hset(self.key, name, message)
#
#     def timeout(self):
#         _timeout = self._connection.hget(self.key, 'timeout')
#         if _timeout:
#             _timeout = int(_timeout) + 1
#         else:
#             _timeout = 1
#         self._connection.hset(self.key, 'timeout', str(_timeout))
#
#     def retry(self):
#         _retry = self._connection.hget(self.key, 'retry')
#         if _retry:
#             _retry = int(_retry) + 1
#         else:
#             _retry = 1
#         self._connection.hset(self.key, 'retry', str(_retry))


class AsyncRunningLogger:
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
            'step-1_kch_id': {
                1: '课程ID设置成功',
                0: '课程ID设置失败'
            },
            'step-3_jxb_ids': {
                1: '教学班ID设置成功',
                0: '教学班ID设置失败'
            },
            'step-2_xkkz_id': {
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

    async def set(self, name: str, success: int):
        await self._connection.hset(self.key, self.wrapper(name), self.messages[name][success])

    async def set_others(self, name: str, message: str):
        await self._connection.hset(self.key, self.wrapper(name), message)

    # async def timeout(self):
    #     _timeout = await self._connection.hget(self.key, 'timeout')
    #     if _timeout:
    #         _timeout = int(_timeout) + 1
    #     else:
    #         _timeout = 1
    #     await self._connection.hset(self.key, 'timeout', str(_timeout))

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
