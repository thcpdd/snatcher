"""
The module of user's session:
    1. The `get_redis_connection` function:
        It will return the redis connection. The result will save in the cache.

    2. The `SessionManager` class:
        It provides some method for controlling user session.
        -- `get` method:
            Return the session string from redis.
            You must provide a port to this method.
        -- `set` method:
            Saving a session to redis.
        -- `all_sessions` method:
            Return all sessions of the user. It's a dictionary.
        -- `has_sessions` method:
            Judging current username is including session or not.
        -- `has_session` method:
            Judging current username is including appoint session or not.
        -- `get_random_session` method:
            Random generating a session.
        -- `close` method:
            Closing current connection of redis.

    3. The `get_session_manager` function:
        Return a session manager of appointing username.

    4. The `AsyncSessionSetter` class:
        You can set a session by this class.
        Usage:
            import asyncio

            setter = AsyncSessionSetter(your_username, your_password, base_url, port)
            cookies, port = asyncio.run(setter.set_session())

    5. The `async_set_session` function:
        A shortcuts for setting the session, but it's a coroutine, could not call directly.

    6. The `set_session` function:
        Providing a way for call the `async_set_session`.

    7. The `check_and_set_session` function:
        If the username haven't session. It will set session for this username.
"""
import base64
from functools import lru_cache
from random import choice

import asyncio
import aiohttp
from Crypto.Cipher import PKCS1_v1_5  # pip install pycryptodome
from Crypto.PublicKey import RSA
from redis import Redis

from snatcher.conf import settings
from .db.mysql import create_failed_data


class SessionManager:
    def __init__(self, username: str):
        self.username = username
        self._session_cache = Redis(**settings.DATABASES['redis']['session'])

    def get(self, port) -> str:
        res = self._session_cache.hget(self.username, port)
        if res is not None:
            return res.decode()
        return ''

    def set(self, cookie, port):
        if cookie and port:
            self._session_cache.hset(self.username, port, cookie)

    def all_sessions(self) -> dict:
        def decode(item: tuple):
            key, value = item
            return key.decode(), value.decode()
        _sessions = self._session_cache.hgetall(self.username)
        return dict(map(decode, _sessions.items()))

    def has_sessions(self) -> bool:
        return self._session_cache.hlen(self.username) > 0

    def has_session(self, port) -> bool:
        return self._session_cache.hexists(self.username, port)

    def get_random_session(self) -> tuple[str, int]:
        port = choice(self._session_cache.hkeys(self.username))
        return self.get(port), int(port.decode())

    def close(self):
        self._session_cache.close()


@lru_cache()
def get_session_manager(username: str):
    return SessionManager(username)


class AsyncSessionSetter:
    def __init__(self, username: str, password: str, base_url, port: int):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.port = port
        self.session = None

    async def get_public_key(self):
        url = self.base_url + '/xtgl/login_getPublicKey.html'
        async with await self.session.get(url) as response:
            return await response.json()

    async def decrypt_password(self):
        public_key = await self.get_public_key()
        n, e = (int(base64.b64decode(value.encode()).hex(), 16)
                for value in public_key.values())
        rsa_key = RSA.construct((n, e))
        cipher = PKCS1_v1_5.new(rsa_key)
        return base64.b64encode(cipher.encrypt(self.password.encode())).decode()

    async def set_session(self):
        """
        默认ClientSession使用的是严格模式的 aiohttp.CookieJar. RFC 2109，
        明确的禁止接受url和ip地址产生的cookie，只能接受 DNS 解析IP产生的cookie。
        可以通过设置aiohttp.CookieJar 的 unsafe=True 来配置
        """
        cookie_jar = aiohttp.CookieJar(unsafe=True)
        timeout = aiohttp.ClientTimeout(total=settings.TIMEOUT)
        try:
            async with aiohttp.ClientSession(cookie_jar=cookie_jar, timeout=timeout) as self.session:
                encrypt_password = await self.decrypt_password()
                url = self.base_url + '/xtgl/login_slogin.html'
                data = {
                    'language': 'zh_CN',
                    'yhm': self.username,
                    'mm': encrypt_password
                }
                async with await self.session.post(url, data=data) as response:
                    if str(response.url) != url:  # 登录成功重定向后url改变
                        cookies = self.session.cookie_jar.filter_cookies(url)
                        return cookies.get('JSESSIONID').value, self.port
                    return '', self.port
        except TimeoutError:
            return '', self.port


async def async_set_session(username, password):
    sessions = [AsyncSessionSetter(username, password, 'http://10.3.132.%s/jwglxt' % port, port)
                for port in settings.PORTS]
    tasks = [asyncio.create_task(session.set_session()) for session in sessions]
    cookies_info = await asyncio.gather(*tasks, return_exceptions=True)
    manager = get_session_manager(username)
    for cookie_info in cookies_info:
        cookie, port = cookie_info
        manager.set(cookie, port)


def set_session(username: str, password: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_set_session(username, password))


def check_and_set_session(username: str, password: str):
    """
    :param username:
    :param password:
    :return: success or not (-1 not success) (1 success)
    """
    manager = get_session_manager(username)
    retry = 0
    while retry < 3:
        if manager.has_sessions():
            break
        set_session(username, password)
        retry += 1
    if not manager.has_sessions():
        create_failed_data(username, '', '', '模拟登录失败', 0)
        return -1
    return 1
