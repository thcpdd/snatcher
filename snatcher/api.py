"""
Some interfaces of this project to start.
"""
import requests
from requests.exceptions import JSONDecodeError

from .tasks import select_course
from .db.mysql import get_db_connection


def physical_education(username: str, password: str, conditions: list, email: str):
    """
    体育课选选课API
    :param username: 学号
    :param password: 密码
    :param conditions: 过滤条件
    :param email: 邮箱
    :return:
    """
    select_course.delay(username, password, conditions, 'PE', email)


def public_choice(username: str, password: str, conditions: list, email: str):
    """
    公选课选课API
    :param username: 学号
    :param password: 密码
    :param conditions: 过滤条件
    :param email: 邮箱
    :return:
    """
    select_course.delay(username, password, conditions, 'PC', email)


def update_pc_course_info():
    url = 'http://10.3.132.10/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512'

    study_year = 2023
    term = 12

    data = {
        'bklx_id': 0,  # 补考类型id
        'xkxnm': study_year,  # 2023学年
        'xkxqm': term,  # 下学期
        'kklxdm': '10',  # 开课类型代码
        'kspage': 1,  # kspage: 1，后来的值：jspage + 1
        'jspage': 10,  # jspage: 10，后来每次 + 10
        'zyfx_id': 'wfx',
        'bh_id': '0425221',  # 班级ID
        'xbm': 1,  # 性别名
        'xslbdm': 'wlb',
        'mzm': '13',
        'xz': 4,
        'ccdm': 3,
        'xsbj': 4,  # 学生标记
        'xqh_id': 3,  # 校区号
        'jg_id': '206',  # 学院id
        'njdm_id': '2022'  # 跟当前学号没有关系，表示当前年级开课情况（体育课）
    }

    headers = {
        'Cookie': 'JSESSIONID=94258A739E2D283AF575FDB08642EB48; route=3d51944d5f53d489f356b638f274e4fb'
    }

    db = get_db_connection()
    cursor = db.cursor()
    sql = """INSERT INTO public_choice_course 
        (`course_name`, `course_id`, `course_no`, `study_year`, `term`)
        VALUES (%s,%s,%s,%s,%s);
    """
    while True:
        response = requests.post(url, data=data, headers=headers)

        try:
            json_data_list = response.json()
        except JSONDecodeError:
            print(response.text)
            return

        if not (temp_list := json_data_list['tmpList']):
            break

        for json_data in temp_list:
            print(json_data)
            cursor.execute(sql, (json_data['kcmc'], json_data['kch_id'], json_data['kch'], study_year, term))
            db.commit()

        # 翻页
        data['kspage'] = int(data['jspage']) + 1
        data['jspage'] = int(data['jspage']) + 10


def update_pe_course_info():
    url = 'http://10.3.132.10/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512'

    study_year = 2023
    term = 12
    grade = '2023'

    data = {
        'bklx_id': 0,
        'xkxnm': study_year,  # 2023学年
        'xkxqm': term,  # 下学期
        'kklxdm': '05',  # 开课类型代码
        'kspage': 1,  # kspage: 1，后来的值：jspage + 1
        'jspage': 10,  # jspage: 10，后来每次 + 10
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
        'njdm_id': grade  # 跟当前学号没有关系，表示当前年级开课情况（体育课）
    }

    headers = {
        'Cookie': 'JSESSIONID=94258A739E2D283AF575FDB08642EB48; route=3d51944d5f53d489f356b638f274e4fb'
    }
    db = get_db_connection()
    cursor = db.cursor()
    sql = """INSERT INTO physical_education_course 
        (`course_name`, `course_id`, `grade`, `study_year`, `term`)
        VALUES (%s,%s,%s,%s,%s);
    """
    while True:
        response = requests.post(url, data=data, headers=headers)

        try:
            json_data_list = response.json()
        except JSONDecodeError:
            print(response.text)
            return

        if not (temp_list := json_data_list['tmpList']):
            break

        for json_data in temp_list:
            print(json_data)
            cursor.execute(sql, (json_data['kcmc'], json_data['kch_id'], grade, study_year, term))
            db.commit()

        # 翻页
        data['kspage'] = int(data['jspage']) + 1
        data['jspage'] = int(data['jspage']) + 10
