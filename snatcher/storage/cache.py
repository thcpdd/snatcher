"""
Some operations of Redis here.
"""
from redis import Redis
from redis.asyncio import Redis as AIORedis

from snatcher.conf import settings


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
    def __init__(self):
        _db_info = settings.DATABASES['redis']['log']
        self._connection = AIORedis(**_db_info)
        self.key = 'runtime-log'
        self.fuel_id = ''
        self.index = ''
        self.count = 1

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def update_logger_info(self, logger_key: str, fuel_id: str = '', index: str = ''):
        exists = await self._connection.exists(logger_key)
        if exists:
            await self._connection.delete(logger_key)
        await self._connection.hset(logger_key, 'fuel_id', fuel_id)
        await self._connection.hset(logger_key, 'index', index)
        self.key = logger_key
        self.fuel_id = fuel_id
        self.index = index
        self.count = 1

    def wrapper(self, name: str):
        return name + '-' + str(self.count)

    @publish_message
    async def set(self, name: str, message: str = '') -> str:
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


def logging(func):
    step_mapping = {
        'set_kch_id': '1',
        'set_xkkz_id': '2',
        'set_jxb_ids': '3',
        'select_course': '4'
    }

    async def _record(*args, **kwargs):
        curr_step = step_mapping[func.__name__]
        code, message = await func(*args, **kwargs)
        selector = args[0]
        logger: AsyncRuntimeLogger = getattr(selector, 'logger')
        await logger.set(curr_step, message)
        return code, message
    return _record


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
    with Redis(**_db_info, decode_responses=True) as conn:
        for _key in conn.keys():
            cache_log = conn.hgetall(_key)
            log = {}
            username, course_name = _key.split('-')
            log.setdefault('course_name', course_name)
            log.setdefault('username', username)
            if 'retry' in cache_log:
                log['retry'] = cache_log.pop('retry')
            if 'error' in cache_log:
                log['error'] = cache_log.pop('error')
            cache_log.pop('index')
            cache_log.pop('fuel_id')
            keys = sorted(cache_log.keys(), reverse=True)
            for key in keys:
                k = key.rsplit('-', maxsplit=1)[0]
                log.setdefault(k, cache_log[key])
            yield log


def export_progress(fuel_id: str, username: str):
    """
    user_log = {
        'username': '2204425143',
        'goals': ['中医药膳与食疗养生', '西方礼仪', '花卉赏析'],
        'progress': [[2, 3], [2, 3], [3, 1]]  # [ 最后一次进度, 尝试次数 ]
    }
    """
    user_log = {
        'username': username,
        'goals': [],
        'progress': []
    }

    _db_info = settings.DATABASES['redis']['log']

    with Redis(**_db_info, decode_responses=True) as conn:
        keys: list = conn.keys(username + '-*')

        if not keys:
            return user_log

        cache_logs = []

        for key in keys:
            cache_log = conn.hgetall(key)
            if cache_log['fuel_id'] == fuel_id:
                course_name = key.split('-')[-1]
                cache_log['course_name'] = course_name
                cache_log.pop('fuel_id')
                cache_logs.append(cache_log)

        if not cache_logs:
            return user_log

        cache_logs = sorted(cache_logs, key=lambda v: v['index'])

        goals = []
        progress = [[] for _ in range(len(cache_logs))]

        for cache_log in cache_logs:
            course_name = cache_log.pop('course_name')
            goals.append(course_name)
            if 'retry' in cache_log:
                cache_log.pop('retry')
            if 'error' in cache_log:
                cache_log.pop('error')
            index = int(cache_log.pop('index')) - 1
            sorted_keys = sorted(cache_log.keys(), reverse=True)
            split_list = sorted_keys[0].split('-')
            last_step, count = int(split_list[0]), int(split_list[1])
            if last_step == 4 and cache_log[sorted_keys[0]] != '选课成功':
                last_step = 3
            progress[index] = [last_step, count]

        user_log['progress'] = progress
        user_log['goals'] = goals

    return user_log
