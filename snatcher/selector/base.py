"""
The course selector base module.
    1. The `ParseStudentID` class:
        It can parse the username. Collecting some special values.

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

    3. The `BaseCourseSelector` class:
        The base class of all course selector
        -- `set_kch_id` method:
            Setting course number id. Must be rewritten.
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

    4. The `CourseSelector` class:
        The father class of course selector.

    5. The `selector_caller` function:
        It will perform relevant logic for a selector instance.
"""
import re

from redis import Redis

from snatcher.conf import settings
from snatcher.db.mysql import (
    create_failed_data,
    create_selected_data
)
from snatcher.mail import send_email


class ParseStudentID:
    def __init__(self, student_id: str) -> None:
        self.student_id = student_id
        self.groups = re.match(r'(\d\d)(\d\d)(\d)(\d\d)(\d)\d*', student_id).groups()

    @property
    def grade(self):
        return self.groups[0]

    @property
    def year(self):
        return '20' + self.grade

    @property
    def major_id(self):
        return self.groups[1] + self.groups[3]

    @property
    def student_class(self):
        return self.grade + self.groups[-1]

    @property
    def class_id(self):
        return self.major_id + self.student_class


class RunningLogs:
    def __init__(self, key):
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

    def set(self, name, success):
        self._connection.hset(self.key, name, self.messages[name][success])

    def set_others(self, name, message):
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


class BaseCourseSelector:
    # 开课类型代码，公选课 10，体育课 05，主修课程 01（英语、思政类），特殊课程 09，其他特殊课程 11
    course_type: str = ''
    term: int = settings.TERM
    select_course_year: int = settings.SELECT_COURSE_YEAR  # 选课学年码

    def __init__(self, username: str):
        self.real_name = '空'
        self.username = username  # 学号
        self.filter_condition = None  # 过滤条件
        self.parser = ParseStudentID(username)  # 解析学号
        self.kch_id = None  # 课程ID
        self.jxb_ids = None  # 教学班ids
        self.xkkz_id = None
        # 获取教学班ids所需的表单数据
        self.get_jxb_ids_data = {
            'bklx_id': 0,  # 补考类型id
            'xqh_id': 3,  # 校区号id
            'jg_id': '206',  # 学院id
            'zyfx_id': 'wfx',  # 专业方向 无方向
            'njdm_id': self.parser.year,  # 年级ID，必须  2022
            'bh_id': self.parser.class_id,  # 班级ID  0425221
            'xbm': 1,  # 性别 男 1  女 2
            'xslbdm': 'wlb',  # 学生类别代码 无类别
            'mzm': 13,  # 民族码
            'xz': 4,  # 学制
            'ccdm': 3,  # 层次代码
            'xsbj': 4,  # 学生标记，国内学生 4
            'xkxnm': self.select_course_year,  # 选课学年码
            'xkxqm': self.term,  # 选课学期码（上下学期，上学期 3，下学期 12）
            'filter_list[0]': self.filter_condition,  # 过滤条件
            'kklxdm': '',  # 开课类型代码，公选课10，体育课05、主修课程01，特殊课程09
            'kch_id': '',  # 课程id
            'xkkz_id': ''  # 选课的时间，课程的类型（主修、体育、特殊、通识）
        }
        # 选课api所需的表单数据
        self.select_course_data = {
            'jxb_ids': '',
            'kch_id': '',
            'qz': 0  # 权重
        }
        self.timeout = settings.TIMEOUT
        self.log = None
        self.session = None
        self.cookies = None
        self.select_course_api = None
        self.index_url = None
        self.jxb_ids_api = None
        self.base_url = None
        self.port = None

    def set_kch_id(self):
        """set course id"""
        raise NotImplementedError('rewritten me')

    def set_xkkz_id(self):
        """set xkkz id"""
        raise NotImplementedError('rewritten me')

    def set_jxb_ids(self):
        """set jxb id"""
        raise NotImplementedError('rewritten me')

    def prepare_for_selecting(self):
        """one by one call: set_kch_id, set_xkkz_id, set_jxb_ids"""
        raise NotImplementedError('rewritten me')

    def simulate_request(self):
        """simulating browser send request"""
        raise NotImplementedError('rewritten me')

    def select(self):
        """outer caller please calling me"""
        raise NotImplementedError('rewritten me')

    def update_or_set_cookie(self, cookie_string: str, port: int):
        """update or set the relative information"""
        if not cookie_string or not port:
            return
        self.cookies = {'JSESSIONID': cookie_string}
        base_url = ''.join(['http:', '//10.3.132.', str(port), '/jwglxt'])
        self.select_course_api = base_url + '/xsxk/zzxkyzbjk_xkBcZyZzxkYzb.html?gnmkdm=N253512'  # 选课api
        self.index_url = base_url + '/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default'  # 选课首页
        self.jxb_ids_api = base_url + '/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512'  # 获取教学班ids的api
        self.base_url = base_url
        self.port = port

    def update_filter_condition(self, filter_condition: str):
        """update filter condition"""
        self.filter_condition = filter_condition
        self.get_jxb_ids_data['filter_list[0]'] = filter_condition
        self.log = RunningLogs(f'{self.username}-{filter_condition}')

    def mark_failed(self, failed_reason: str):
        """create a fail data into mysql"""
        create_failed_data(
            self.username,
            self.real_name,
            self.log.key,
            failed_reason,
            self.port
        )


class CourseSelector(BaseCourseSelector):
    """
    The father class of all course selector.
    Including synchronous course selector and asynchronous course selector.
    """


def selector_caller(
    conditions: list,
    username: str,
    email: str,
    selector: CourseSelector
):
    for condition in conditions:
        selector.update_filter_condition(condition)
        result = selector.select()
        create_selected_data(username, email, selector.real_name, selector.log.key)
        if result == 1:
            send_email(email, username, selector.real_name)
            break
