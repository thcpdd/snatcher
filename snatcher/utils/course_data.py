"""
Some tools to get course data in this module:
    1. The `ParseStudentID` class:
        It can parse the username. Collecting some special values.

    2. The `update_data` function:
        Updating course information to mysql.
        If the argument `grade` is null, all data will write to `public_choice_course` table.
        Otherwise, all data will write to `physical_education_course` table.

    3. The `update_pc_data` function:
        Updating the 'PC' course data to database.

    4. The `update_pe_data` function:
        Updating the 'PE' course data to database.
"""
import re

import aiohttp
from aiohttp.client_exceptions import ContentTypeError

from snatcher.conf import settings
from snatcher.storage.mongo import collections


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


async def update_data(port: str, cookie: str, grade: int = None):
    study_year = settings.SELECT_COURSE_YEAR
    term = settings.TERM

    url = 'http://10.3.132.%s/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512' % port
    data = {
        'bklx_id': 0,
        'xkxnm': study_year,
        'xkxqm': term,
        'kklxdm': '',
        'kspage': 1,  # kspage: 1, after: jspage + 1
        'jspage': 500,  # jspage(Every page size, as far as possible is max): 10, after: jspage + 10
    }
    headers = {
        'Cookie': 'JSESSIONID=%s' % cookie
    }
    if grade is not None:
        collection = collections['pe']
        data['njdm_id'] = grade  # add a must field
        data['kklxdm'] = '05'
        data.update({
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
        })
    else:
        collection = collections['pc']
        data['kklxdm'] = '10'

    async with aiohttp.ClientSession() as session:
        response = await session.post(url, data=data, headers=headers)

    try:
        json_data_list = await response.json()
    except ContentTypeError:
        print(response.text)
        return

    if not (temp_list := json_data_list['tmpList']):
        return

    if grade is not None:
        for json_data in temp_list:
            print(json_data)
            collection.create(
                course_name=json_data['kcmc'],
                course_id=json_data['kch_id'],
                jxb_id=json_data['jxb_id'],
                jxbmc=json_data['jxbmc'],
                grade=grade
            )
    else:
        for json_data in temp_list:
            print(json_data)
            collection.create(
                course_name=json_data['kcmc'],
                course_id=json_data['kch_id'],
                jxb_id=json_data['jxb_id'],
                jxbmc=json_data['jxbmc']
            )


async def update_pc_data(port: str, cookie: str):
    await update_data(port, cookie)


async def update_pe_data(port: str, cookie: str, grade: int):
    await update_data(port, cookie, grade)
