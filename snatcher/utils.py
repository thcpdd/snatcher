"""
Some tools in this module:
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

    3. The `update_data` function:
        Updating course information to mysql.
        If the argument `grade` is null, all data will write to `public_choice_course` table.
        Otherwise, all data will write to `physical_education_course` table.

    4. The `update_pc_data` function:
        Updating the 'PC' course data to database.

    5. The `update_pe_data` function:
        Updating the 'PE' course data to database.
"""
import re

import requests
from requests.exceptions import JSONDecodeError
from redis import Redis

from snatcher.conf import settings
from snatcher.db.mysql import get_db_connection


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
