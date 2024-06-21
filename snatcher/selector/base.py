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

from aiohttp import ClientSession
from requests import Session

from snatcher.conf import settings
from snatcher.storage.mysql import (
    fd_querier,
    scd_querier,
)
from snatcher.session import SessionManager
from snatcher.postman.mail import send_email
from snatcher.storage.cache import AsyncRunningLogger


class BaseCourseSelector:
    # 开课类型代码，公选课 10，体育课 05，主修课程 01（英语、思政类），特殊课程 09，其他特殊课程 11
    course_type: str = ''
    term: int = settings.TERM
    select_course_year: int = settings.SELECT_COURSE_YEAR  # 选课学年码

    def __init__(self, username: str):
        self.username: str = username  # 学号
        # 获取教学班ids所需的表单数据
        self.get_jxb_ids_data: dict = {
            'bklx_id': 0,  # 补考类型id
            'njdm_id': '20' + username[:2],  # 年级ID，必须  2022
            'xkxnm': self.select_course_year,  # 选课学年码
            'xkxqm': self.term,  # 选课学期码（上下学期，上学期 3，下学期 12）
            'kklxdm': '',  # 开课类型代码，公选课10，体育课05、主修课程01，特殊课程09
            'kch_id': '',  # 课程id
            'xkkz_id': ''  # 选课的时间，课程的类型（主修、体育、特殊、通识）
        }
        # 选课api所需的表单数据
        self.select_course_data: dict = {
            'jxb_ids': '',
            'kch_id': '',
            'qz': 0  # 权重
        }
        self.timeout: int = settings.TIMEOUT
        self.sub_select_course_api: str = '/xsxk/zzxkyzbjk_xkBcZyZzxkYzb.html?gnmkdm=N253512'
        self.sub_index_url: str = '/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default'
        self.sub_jxb_ids_api: str = '/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512'
        self.select_course_api: Optional[str] = None  # 选课api
        self.index_url: Optional[str] = None  # 选课首页
        self.jxb_ids_api: Optional[str] = None  # 获取教学班ids的api
        self.log: Optional[AsyncRunningLogger] = None
        self.real_name: Optional[str] = None
        self.log_key: Optional[str] = None
        self.session: Optional[Session, ClientSession] = None
        self.session_manager: Optional[SessionManager] = None
        self.cookies: Optional[dict] = None
        self.base_url: Optional[str] = None
        self.port: Optional[str] = None
        self.kch_id: Optional[str] = None  # 课程ID
        self.jxb_ids: Optional[str] = None  # 教学班ids
        self.xkkz_id: Optional[str] = None
        self.latest_selected_data_id: Optional[int] = None

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

    def update_selector_info(self, course_name: str, course_id: str, email: str):
        """Updating relative information."""
        self.real_name = course_name
        self.kch_id = course_id
        self.log_key = f'{self.username}-{course_name}'
        row_id = scd_querier.insert(self.username, email, course_name, self.log_key)
        self.latest_selected_data_id = row_id

    def mark_failed(self, failed_reason: str):
        """Creating a failed data into mysql."""
        send_email(
            '1834763300@qq.com',
            self.username,
            self.real_name,
            False,
            failed_reason
        )
        fd_querier.insert(
            self.username,
            self.real_name,
            self.log.key,
            failed_reason,
            int(self.port)
        )


class CourseSelector(BaseCourseSelector):
    """
    The father class of all course selector.
    Including synchronous course selector and asynchronous course selector.
    """
