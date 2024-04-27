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


class PortWeightManager:
    def __init__(self):
        self.weights_cache = None

    def get_optimal_port(self):
        rank = 0

        def inner() -> list:
            nonlocal rank

            port_list = self.weights_cache.zrevrange('weights', rank, rank)
            rank += 1
            return port_list
        return inner

    def decrease_weight(self, port: str, decrease_size: int | float = 20):
        weight = self.weights_cache.zscore('weights', port)
        self.weights_cache.zadd('weights', {port: weight - decrease_size})

    def increase_weight(self, port: str, increase_size: int | float = 10):
        weight = self.weights_cache.zscore('weights', port)
        self.weights_cache.zadd('weights', {port: weight + increase_size})

    def __enter__(self):
        self.weights_cache = Redis(**settings.DATABASES['redis']['weights'], decode_responses=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.weights_cache.close()


def optimal_port_generator():
    with PortWeightManager() as manager:
        optimal_port = manager.get_optimal_port()
        while port_list := optimal_port():
            yield port_list[0]


def decreasing_weight(port: str, decrease_size: int | float = 20):
    with PortWeightManager() as manager:
        manager.decrease_weight(port, decrease_size)


def increasing_weight(port: str, increase_size: int | float = 10):
    with PortWeightManager() as manager:
        manager.increase_weight(port, increase_size)


class RunningLogs:
    def __init__(self, key: str):
        _db_info = settings.DATABASES['redis']['log']
        self._connection = Redis(**_db_info)
        self.key = key
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

    def set(self, name: str, success: int):
        self._connection.hset(self.key, name, self.messages[name][success])

    def set_others(self, name: str, message: str):
        self._connection.hset(self.key, name, message)

    def timeout(self):
        _timeout = self._connection.hget(self.key, 'timeout')
        if _timeout:
            _timeout = int(_timeout) + 1
        else:
            _timeout = 1
        self._connection.hset(self.key, 'timeout', str(_timeout))

    def retry(self):
        _retry = self._connection.hget(self.key, 'retry')
        if _retry:
            _retry = int(_retry) + 1
        else:
            _retry = 1
        self._connection.hset(self.key, 'retry', str(_retry))


class AsyncRunningLogs:
    """
    You must call close method before function was garbage collected.
    Example:
        The base usage in coroutine function:
            async def test():
                logs = AsyncRunningLogs('your_key')
                ...  # your operations
                await logs.close()  # It is must !!!
        You can also use it as a context manager in the coroutine function:
            async def test():
                async with AsyncRunningLogs('your_key') as logs:
                    ...  # your operations
    """
    def __init__(self, key: str):
        _db_info = settings.DATABASES['redis']['log']
        self._connection = AIORedis(**_db_info)
        self.key = key
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

    async def set(self, name: str, success: int):
        await self._connection.hset(self.key, name, self.messages[name][success])

    async def set_others(self, name: str, message: str):
        await self._connection.hset(self.key, name, message)

    async def timeout(self):
        _timeout = await self._connection.hget(self.key, 'timeout')
        if _timeout:
            _timeout = int(_timeout) + 1
        else:
            _timeout = 1
        await self._connection.hset(self.key, 'timeout', str(_timeout))

    async def retry(self):
        _retry = await self._connection.hget(self.key, 'retry')
        if _retry:
            _retry = int(_retry) + 1
        else:
            _retry = 1
        await self._connection.hset(self.key, 'retry', str(_retry))

    async def close(self):
        """you must call this before function was garbage collected."""
        await self._connection.aclose()
