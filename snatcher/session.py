"""
The module of user's session:
    1. The `SessionManager` class:
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
        -- `get_session_by_weight`:
            Generating a session by port weight.
        -- `get_random_session` method:
            Random generating a session.
        -- `close` method:
            Closing current connection of redis.

    2. The `get_session_manager` function:
        Return a session manager of appointing username.

    3. The `AsyncSessionSetter` class:
        You can set a session by this class.
        Usage:
            import asyncio

            setter = AsyncSessionSetter(your_username, your_password, base_url, port)
            cookies, port = asyncio.run(setter.set_session())

    4. The `async_set_session` function:
        A shortcuts for setting the session, but it's a coroutine, could not call directly.

    5. The `set_session` function:
        Providing a sync way for call the `async_set_session`.

    6. The `check_and_set_session` function:
        If the username haven't session. It will set session for this username.

    7. The `async_check_and_set_session` function:
        An async way to check and set session.
"""
import base64
from functools import lru_cache
from random import choice
from yarl import URL

import asyncio
import aiohttp
from Crypto.Cipher import PKCS1_v1_5  # pip install pycryptodome
from Crypto.PublicKey import RSA
from redis import Redis

from snatcher.conf import settings
from snatcher.storage.mysql import fd_querier
from snatcher.storage.cache import optimal_port_generator
from snatcher.postman.mail import send_email


class SessionManager:
    def __init__(self, username: str):
        self.username = username
        self._session_cache = Redis(**settings.DATABASES['redis']['session'], decode_responses=True)

    def get(self, port: str) -> str:
        res = self._session_cache.hget(self.username, port)
        if res is not None:
            return res
        return ''

    def save_cookie(self, cookie: str, port: str):
        if cookie and port:
            self._session_cache.hset(self.username, port, cookie)

    def save_xkkz_id(self, xkkz_id: str):
        _grade = self.username[:2]
        if not self._session_cache.hexists(self.username, 'xkkz_id'):
            self._session_cache.hset(self.username, 'xkkz_id', xkkz_id)
        if not self._session_cache.hexists('xkkz_id', _grade):
            self._session_cache.hset('xkkz_id', _grade, xkkz_id)

    def get_xkkz_id(self) -> str:
        _grade = self.username[:2]
        if cache_xkkz_id := self._session_cache.hget('xkkz_id', _grade):
            return cache_xkkz_id
        if user_xkkz_id := self._session_cache.hget(self.username, 'xkkz_id'):
            return user_xkkz_id
        return ''

    def all_sessions(self) -> dict:
        return self._session_cache.hgetall(self.username)

    def has_sessions(self) -> bool:
        return self._session_cache.hlen(self.username) > 0

    def has_session(self, port: str) -> bool:
        return self._session_cache.hexists(self.username, port)

    def get_session_by_weight(self) -> tuple[str, str]:
        for port in optimal_port_generator():
            if self.has_session(port):
                return self.get(port), port
        return self.get_random_session()

    def get_random_session(self) -> tuple[str, str]:
        port = choice(self._session_cache.hkeys(self.username))
        return self.get(port), port

    def close(self):
        self._session_cache.close()


@lru_cache()
def get_session_manager(username: str):
    return SessionManager(username)


class AsyncSessionSetter:
    def __init__(self, username: str, password: str, base_url: str, port: str):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.port = port
        self.session = None

    async def get_public_key(self):
        url = self.base_url + '/xtgl/login_getPublicKey.html'
        async with await self.session.get(url) as response:
            return await response.json()

    async def encrypt_password(self):
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
        timeout = aiohttp.ClientTimeout(total=settings.SETTING_SESSION_TIMEOUT)
        try:
            async with aiohttp.ClientSession(cookie_jar=cookie_jar, timeout=timeout) as self.session:
                encrypt_password = await self.encrypt_password()
                url = self.base_url + '/xtgl/login_slogin.html'
                data = {
                    'language': 'zh_CN',
                    'yhm': self.username,
                    'mm': encrypt_password
                }
                async with await self.session.post(url, data=data, allow_redirects=False) as response:
                    if response.status == 302:  # 302表示将要重定向，登录成功
                        cookies = self.session.cookie_jar.filter_cookies(URL(url))
                        return cookies.get('JSESSIONID').value, self.port
                    return '', self.port
        except TimeoutError:
            return '', self.port


async def async_set_session(username: str, password: str):
    if settings.countdown() > 0:
        # 没有开始选课时，获取所有主机的 Cookie
        sessions = [AsyncSessionSetter(username, password, 'http://10.3.132.%s/jwglxt' % port, port)
                    for port in settings.PORTS]
    else:
        # 开始选课时，只获取一个主机的 Cookie
        port = next(optimal_port_generator())
        sessions = [AsyncSessionSetter(username, password, 'http://10.3.132.%s/jwglxt' % port, port)]
    tasks = [asyncio.create_task(session.set_session()) for session in sessions]
    cookies_info = await asyncio.gather(*tasks, return_exceptions=True)
    manager = get_session_manager(username)
    for cookie_info in cookies_info:
        cookie, port = cookie_info
        manager.save_cookie(cookie, port)


# def set_session(username: str, password: str):
#     from asgiref.sync import async_to_sync
#
#     async_to_sync(async_set_session)(username, password)


# def check_and_set_session(username: str, password: str):
#     """
#     :param username:
#     :param password:
#     :return: success or not (-1 not success) (1 success)
#     """
#     manager = get_session_manager(username)
#     retry = 0
#     while retry < 3:
#         if manager.has_sessions():
#             break
#         set_session(username, password)
#         retry += 1
#     if not manager.has_sessions():
#         fd_querier.insert(username, '', '', '模拟登录失败', 0)
#         send_email('1834763300@qq.com', username, '', False, '模拟登录失败')
#         return -1
#     return 1


async def async_check_and_set_session(username: str, password: str):
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
        await async_set_session(username, password)
        retry += 1
    if not manager.has_sessions():
        fd_querier.insert(username, '', '', '模拟登录失败', 0)
        send_email('1834763300@qq.com', username, '', False, '模拟登录失败')
        return -1
    return 1
