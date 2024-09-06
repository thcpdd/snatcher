"""
The module of user's session:
    1. The `SessionManager` class:
        It provides some methods for controlling user session.

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

    5. The `async_check_and_set_session` function:
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

    def save_xkkz_id(self, xkkz_id: str, course_type: str):
        _grade = self.username[:2]
        if not self._session_cache.hexists(course_type + '_xkkz_id', _grade):
            self._session_cache.hset(course_type + '_xkkz_id', _grade, xkkz_id)

    def get_xkkz_id(self, course_type: str) -> str:
        _grade = self.username[:2]
        if cache_xkkz_id := self._session_cache.hget(course_type + '_xkkz_id', _grade):
            return cache_xkkz_id
        return ''

    def all_sessions(self) -> dict:
        return self._session_cache.hgetall(self.username)

    def has_sessions(self) -> bool:
        return self._session_cache.hlen(self.username) > 0

    def has_session(self, port: str) -> bool:
        return self._session_cache.hexists(self.username, port)

    def get_random_session(self) -> tuple[str, str]:
        port = choice(self._session_cache.hkeys(self.username))
        return self.get(port), port

    def close(self):
        self._session_cache.close()


@lru_cache()
def get_session_manager(username: str):
    return SessionManager(username)


class AsyncSessionSetter:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        cookie_jar = aiohttp.CookieJar(unsafe=True)
        timeout = aiohttp.ClientTimeout(total=settings.SETTING_SESSION_TIMEOUT)
        self.session = aiohttp.ClientSession(cookie_jar=cookie_jar, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            await self.session.close()

    async def get_public_key(self, base_url: str):
        url = base_url + '/xtgl/login_getPublicKey.html'
        async with await self.session.get(url) as response:
            return await response.json()

    async def encrypt_password(self, base_url: str):
        public_key = await self.get_public_key(base_url)
        n, e = (int(base64.b64decode(value.encode()).hex(), 16)
                for value in public_key.values())
        rsa_key = RSA.construct((n, e))
        cipher = PKCS1_v1_5.new(rsa_key)
        return base64.b64encode(cipher.encrypt(self.password.encode())).decode()

    async def set_session(self, base_url: str, port: str):
        """
        默认ClientSession使用的是严格模式的 aiohttp.CookieJar. RFC 2109，
        明确的禁止接受url和ip地址产生的cookie，只能接受 DNS 解析IP产生的cookie。
        可以通过设置aiohttp.CookieJar 的 unsafe=True 来配置
        """
        url = base_url + '/xtgl/login_slogin.html'
        try:
            encrypt_password = await self.encrypt_password(base_url)
            data = {'language': 'zh_CN', 'yhm': self.username, 'mm': encrypt_password}
            response = await self.session.post(url, data=data, allow_redirects=False)
        except Exception as exception:
            print(exception)
            return '', port
        else:
            if response.status == 302:  # 302表示将要重定向，登录成功
                cookies = self.session.cookie_jar.filter_cookies(URL(url))
                return cookies.get('JSESSIONID').value, port
            return '', port


async def async_set_session(username: str, password: str):
    if settings.countdown() > 0:  # 没有开始选课时，获取所有主机的 Cookie
        ports = settings.PORTS
    else:  # 开始选课时，只获取一个主机的 Cookie
        ports = [choice(settings.PORTS)]

    base_url = 'http://10.3.132.%s/jwglxt'

    async with AsyncSessionSetter(username, password) as setter:
        tasks = []

        for port in ports:
            set_session = setter.set_session(base_url % port, port)
            task = asyncio.create_task(set_session)
            tasks.append(task)

        cookies_info = await asyncio.gather(*tasks, return_exceptions=True)

    manager = get_session_manager(username)
    for cookie, port in cookies_info:
        manager.save_cookie(cookie, port)


async def async_check_and_set_session(username: str, password: str):
    """
    :param username:
    :param password:
    :return: success or not (-1 not success) (1 success)
    """
    manager = get_session_manager(username)
    if manager.has_sessions():
        return 1
    for _ in range(3):
        await async_set_session(username, password)
        if manager.has_sessions():
            return 1
    return -1
