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
from yarl import URL

from aiohttp import ClientSession, ClientTimeout, CookieJar

from snatcher.conf import settings
from snatcher.session import SessionManager, get_session_manager
from snatcher.storage.cache import AsyncRuntimeLogger, logging
from snatcher.message import Messages, MessageType


class BaseCourseSelector:
    # 开课类型代码，公选课 10，体育课 05，主修课程 01（英语、思政类），特殊课程 09，其他特殊课程 11
    course_type: str = ''
    term: int = settings.TERM
    select_course_year: int = settings.SELECT_COURSE_YEAR  # 选课学年码

    def __init__(self, username: str, fuel_id: str = None):
        self.username: str = username
        self.get_jxb_ids_data: dict = {
            'bklx_id': 0,
            'njdm_id': '20' + username[:2],
            'xkxnm': self.select_course_year,
            'xkxqm': self.term,
            'kklxdm': self.course_type,
            'kch_id': '',
            'xkkz_id': ''
        }
        self.select_course_data: dict = {
            'jxb_ids': '',
            'kch_id': '',
            'qz': 0
        }
        self.sub_select_course_api: str = '/xsxk/zzxkyzbjk_xkBcZyZzxkYzb.html?gnmkdm=N253512'
        self.sub_index_url: str = '/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default'
        self.sub_jxb_ids_api: str = '/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512'
        self.select_course_api: str = ''  # 选课api
        self.index_url: str = ''  # 选课首页
        self.jxb_ids_api: str = ''  # 获取教学班ids的api
        self.logger: AsyncRuntimeLogger | None = None
        self.session: ClientSession | None = None
        self.session_manager: SessionManager | None = None
        self.cookies: dict[str, str] = {}
        self.base_url: str = ''
        self.port: str = ''
        self.kch_id: str = ''  # 课程ID
        self.jxb_ids: str = ''  # 教学班ids
        self.jxb_id: str = ''
        self.xkkz_id: str = ''
        self.fuel_id: str = fuel_id or ''
        self.index: int = 1
        self.jg_id: str = ''
        self.extra_jxb_ids_params: dict[str, str] = {}

    async def __aenter__(self):
        cookie_jar = CookieJar(unsafe=True)
        timeout = ClientTimeout(total=settings.TIMEOUT)
        self.session = ClientSession(cookie_jar=cookie_jar, timeout=timeout)
        self.session_manager = get_session_manager(self.username)
        self.logger = AsyncRuntimeLogger()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.logger.close()

    @logging
    async def set_kch_id(self) -> MessageType:
        return Messages.KCH_ID_SUCCESS

    @logging
    async def set_xkkz_id(self) -> MessageType:
        """Setting xkkz id."""
        raise NotImplementedError

    @logging
    async def set_jxb_ids(self) -> MessageType:
        """Setting jxb id."""
        raise NotImplementedError

    @logging
    async def select_course(self) -> MessageType:
        raise NotImplementedError

    async def _select(self) -> MessageType:
        """One by one call: set_xkkz_id, set_jxb_ids."""
        raise NotImplementedError

    def _construct_jxb_ids_params(self):
        raise NotImplementedError

    def _set_jxb_ids(self, do_jxb_id_list: list[dict]) -> MessageType:
        raise NotImplementedError

    async def select(self) -> MessageType:
        """Outer caller please calling me."""
        raise NotImplementedError

    def update_cookie(self):
        """Updating or set the relative information."""
        cookie_string, port = self.session_manager.get_random_session()
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

    async def update_selector_info(
        self,
        course_name: str,
        course_id: str,
        jxb_id: str,
        logger_key: str = ''
    ):
        """Updating relative information."""
        self.kch_id = course_id
        self.jxb_id = jxb_id
        logger_key = logger_key or self.username + '-' + course_name
        await self.logger.update_logger_info(logger_key, self.fuel_id, str(self.index))
        self.index += 1
