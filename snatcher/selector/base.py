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

    5. The `selector_performer` function:
        It will perform relevant logic for a selector instance.

    6. The `update_data` function:
        Updating course information to mysql.
        If the argument `grade` is null, all data will write to `public_choice_course` table.
        Otherwise, all data will write to `physical_education_course` table.

    7. The `update_pc_data` function:
        Updating the 'PC' course data to database.

    8. The `update_pe_data` function:
        Updating the 'PE' course data to database.
"""
import re

import requests
from requests.exceptions import JSONDecodeError
from redis import Redis

from snatcher.conf import settings
from snatcher.db.mysql import (
    create_failed_data,
    create_selected_data,
    mark_verify_code_is_used,
    get_db_connection
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
        self.username = username  # 学号
        self.parser = ParseStudentID(username)  # 解析学号
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
        self.real_name = None
        self.log = None
        self.session = None
        self.cookies = None
        self.select_course_api = None
        self.index_url = None
        self.jxb_ids_api = None
        self.base_url = None
        self.port = None
        self.kch_id = None  # 课程ID
        self.jxb_ids = None  # 教学班ids
        self.xkkz_id = None

    def set_kch_id(self):
        """set course id"""
        raise NotImplementedError('rewrite me')

    def set_xkkz_id(self):
        """set xkkz id"""
        raise NotImplementedError('rewrite me')

    def set_jxb_ids(self):
        """set jxb id"""
        raise NotImplementedError('rewrite me')

    def prepare_for_selecting(self):
        """one by one call: set_kch_id, set_xkkz_id, set_jxb_ids"""
        raise NotImplementedError('rewrite me')

    def simulate_request(self):
        """simulating browser send request"""
        raise NotImplementedError('rewrite me')

    def select(self):
        """outer caller please calling me"""
        raise NotImplementedError('rewrite me')

    def update_or_set_cookie(self, cookie_string: str, port: str):
        """update or set the relative information"""
        if not cookie_string or not port:
            return
        self.cookies = {'JSESSIONID': cookie_string}
        base_url = ''.join(['http:', '//10.3.132.', port, '/jwglxt'])
        self.select_course_api = base_url + '/xsxk/zzxkyzbjk_xkBcZyZzxkYzb.html?gnmkdm=N253512'  # 选课api
        self.index_url = base_url + '/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default'  # 选课首页
        self.jxb_ids_api = base_url + '/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512'  # 获取教学班ids的api
        self.base_url = base_url
        self.port = port

    def update_selector_info(self, course_name: str, course_id: str, email: str):
        """update relative information"""
        self.real_name = course_name
        self.kch_id = course_id
        self.log = RunningLogs(f'{self.username}-{course_name}')
        create_selected_data(self.username, email, course_name, self.log.key)

    def mark_failed(self, failed_reason: str):
        """create a fail data into mysql"""
        send_email(
            '1834763300@qq.com',
            self.username,
            self.real_name,
            False,
            failed_reason
        )
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


def selector_performer(
    email: str,
    verify_code: str,
    goals: list[tuple[str, str]],
    selector: CourseSelector,
):
    for course_name, course_id in goals:
        selector.update_selector_info(course_name, course_id, email)
        result = selector.select()
        if result == 1:
            mark_verify_code_is_used(selector.username, verify_code)
            send_email(email, selector.username, course_name)
            break


def update_data(grade: str = None):
    study_year = settings.SELECT_COURSE_YEAR
    term = settings.TERM

    url = 'http://10.3.132.10/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512'
    data = {
        'bklx_id': 0,
        'xkxnm': study_year,
        'xkxqm': term,
        'kklxdm': '',
        'kspage': 1,  # kspage: 1, after: jspage + 1
        'jspage': 10,  # jspage: 10, after: jspage + 10
        'zyfx_id': 'wfx',
        'bh_id': '0425221',
        'xbm': 1,
        'xslbdm': 'wlb',
        'mzm': '13',
        'xz': 4,
        'ccdm': 3,
        'xsbj': 4,
        'xqh_id': 3,
        'jg_id': '206',
    }
    headers = {
        'Cookie': 'JSESSIONID=7A7572FCAEBCA0E7D6CFDC05CC96758F; route=f24d04cc10e92fdab9790b41504f5b47'
    }
    if grade is not None:
        data['njdm_id'] = grade  # add a must field
        data['kklxdm'] = '05'
        sql = """INSERT INTO pe 
            (`course_name`, `course_id`, `grade`, `study_year`, `term`)
            VALUES (%s,%s,%s,%s,%s);
        """
    else:
        data['kklxdm'] = '10'
        sql = """INSERT INTO pc 
            (`course_name`, `course_id`, `course_no`, `study_year`, `term`, `period`)
            VALUES (%s,%s,%s,%s,%s,%s);
        """
    db = get_db_connection()
    cursor = db.cursor()

    while True:
        response = requests.post(url, data=data, headers=headers)

        try:
            json_data_list = response.json()
        except JSONDecodeError:
            print(response.text)
            return

        if not (temp_list := json_data_list['tmpList']):
            break

        if grade is not None:
            for json_data in temp_list:
                print(json_data)
                cursor.execute(sql, (json_data['kcmc'], json_data['kch_id'], grade, study_year, term))
        else:
            for json_data in temp_list:
                print(json_data)
                cursor.execute(sql, (json_data['kcmc'], json_data['kch_id'], json_data['kch'], study_year, term,
                                     settings.PERIOD))

        db.commit()

        # next page
        data['kspage'] = data['jspage'] + 1
        data['jspage'] += 10


def update_pc_data():
    update_data()


def update_pe_data(grade: str):
    update_data(grade)
