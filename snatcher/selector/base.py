"""
The course selector base module.
    1. The `BaseCourseSelector` class:
        The base class of all course selector
        -- `set_xkkz_id` method:
            Setting 'xkkz' id. Must be rewritten.
        -- `set_jxb_ids` method:
            Setting 'jxb' id. Must be rewritten.
        -- `prepare_for_selecting` method:
            It will be called before sending a request. Must be rewritten.
        -- `simulate_request` method:
            The specific logic of selecting course. Must be rewritten.
        -- `select` method:
            A method for outer caller. Must be rewritten.

    2. The `CourseSelector` class:
        The father class of course selector.
"""
from typing import Optional
from yarl import URL

from aiohttp import ClientSession, ClientTimeout, CookieJar

from snatcher.conf import settings
from snatcher.session import SessionManager, get_session_manager
from snatcher.storage.cache import AsyncRuntimeLogger


class BaseCourseSelector:
    # 开课类型代码，公选课 10，体育课 05，主修课程 01（英语、思政类），特殊课程 09，其他特殊课程 11
    course_type: str = ''
    term: int = settings.TERM
    select_course_year: int = settings.SELECT_COURSE_YEAR  # 选课学年码

    def __init__(self, username: str, fuel_id: str = None):
        self.username: str = username  # 学号
        # 获取教学班 ids 所需的表单数据
        self.get_jxb_ids_data: dict = {
            'bklx_id': 0,  # 补考类型id
            'njdm_id': '20' + username[:2],  # 年级ID，必须  2022
            'xkxnm': self.select_course_year,  # 选课学年码
            'xkxqm': self.term,  # 选课学期码（上下学期，上学期 3，下学期 12）
            'kklxdm': '',  # 开课类型代码，公选课10，体育课05、主修课程01，特殊课程09
            'kch_id': '',  # 课程id
            'xkkz_id': ''  # 选课的时间，课程的类型（主修、体育、特殊、通识）
        }
        # 选课 api 所需的表单数据
        self.select_course_data: dict = {
            'jxb_ids': '',
            'kch_id': '',
            'qz': 0  # 权重
        }
        self.timeout: Optional[int, ClientTimeout] = settings.TIMEOUT
        self.sub_select_course_api: str = '/xsxk/zzxkyzbjk_xkBcZyZzxkYzb.html?gnmkdm=N253512'
        self.sub_index_url: str = '/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default'
        self.sub_jxb_ids_api: str = '/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512'
        self.select_course_api: Optional[str] = None  # 选课api
        self.index_url: Optional[str] = None  # 选课首页
        self.jxb_ids_api: Optional[str] = None  # 获取教学班ids的api
        self.logger: Optional[AsyncRuntimeLogger] = None
        self.real_name: Optional[str] = None
        self.session: Optional[ClientSession] = None
        self.session_manager: Optional[SessionManager] = None
        self.cookies: Optional[dict] = None
        self.base_url: Optional[str] = None
        self.port: Optional[str] = None
        self.kch_id: Optional[str] = None  # 课程ID
        self.jxb_ids: Optional[str] = None  # 教学班ids
        self.xkkz_id: Optional[str] = None
        self.fuel_id: Optional[str] = fuel_id or ''
        self.index: Optional[int] = None

    async def __aenter__(self):
        cookie_jar = CookieJar(unsafe=True)
        if isinstance(self.timeout, int):
            self.timeout = ClientTimeout(total=self.timeout)
        self.session = ClientSession(cookie_jar=cookie_jar, timeout=self.timeout)
        self.session_manager = get_session_manager(self.username)
        self.logger = AsyncRuntimeLogger()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.logger.close()
        self.session_manager.close()


class CourseSelector(BaseCourseSelector):
    """
    The father class of all course selector.
    Including synchronous course selector and asynchronous course selector.

    For the following methods, you should achieve their in your subclass:
         1. `set_xkkz_id`
         2. `set_jxb_ids`
         3. `prepare_for_selecting`
         4. `simulate_request`
         5. `select`
    """
    def set_xkkz_id(self):
        """Setting xkkz id."""
        raise NotImplementedError

    def set_jxb_ids(self):
        """Setting jxb id."""
        raise NotImplementedError

    def prepare_for_selecting(self):
        """One by one call: set_xkkz_id, set_jxb_ids."""
        raise NotImplementedError

    def simulate_request(self):
        """Simulating browser send request."""
        raise NotImplementedError

    def select(self):
        """Outer caller please calling me."""
        raise NotImplementedError

    def update_or_set_cookie(self, cookie_string: str, port: str):
        """Updating or set the relative information."""
        if not cookie_string or not port:
            return
        self.cookies = {'JSESSIONID': cookie_string}
        base_url = ''.join(['http:', '//10.3.132.', port, '/jwglxt'])
        self.select_course_api = base_url + self.sub_select_course_api
        self.index_url = base_url + self.sub_index_url
        self.jxb_ids_api = base_url + self.sub_jxb_ids_api
        self.base_url = base_url
        self.port = port
        self.session.cookie_jar.update_cookies(self.cookies, URL(base_url))

    async def update_selector_info(self, course_name: str, course_id: str, logger_key: str):
        """Updating relative information."""
        self.real_name = course_name
        self.kch_id = course_id
        if self.index is None:
            self.index = 1
        else:
            self.index += 1
        await self.logger.update_logger_info(logger_key, self.fuel_id, str(self.index))
