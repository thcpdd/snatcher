"""
Some interfaces of this project to start.
    1. The `physical_education` function:
        A interface to send a 'PE' select course task to celery task queue.

    2. The `public_choice` function:
        A interface to send a 'PC' select course task to celery task queue.

    3. The `update_pc_course_info` function:
        Updating the 'PC' course info.
        You should mind two variable in function inner:
            `study_year`: current study year, it could change every term.
            `term`: it only has two values. next term is 12, last term is 3.
            `headers`: it must contain effective cookie information for current url.

    4. The `update_pr_course_info` function:
        Updating the 'PE' course info.
        You should mind three variable in function inner:
            `study_year`: current study year, it could change every term.
            `term`: it only has two values. next term is 12, last term is 3.
            `headers`: it must contain effective cookie information for current url.
            `grade`: it decides every grade course information.
"""
import requests
from requests.exceptions import JSONDecodeError

from .tasks import select_course
from .db.mysql import get_db_connection


def physical_education(username: str, password: str, conditions: list, email: str):
    select_course.delay(username, password, conditions, 'PE', email)


def public_choice(username: str, password: str, conditions: list, email: str):
    select_course.delay(username, password, conditions, 'PC', email)


def update_pc_course_info():
    url = 'http://10.3.132.10/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512'

    study_year = 2023
    term = 12

    data = {
        'bklx_id': 0,
        'xkxnm': study_year,
        'xkxqm': term,
        'kklxdm': '10',
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
        'njdm_id': '2022'
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

        # next page
        data['kspage'] = int(data['jspage']) + 1
        data['jspage'] = int(data['jspage']) + 10


def update_pe_course_info():
    url = 'http://10.3.132.10/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512'

    study_year = 2023
    term = 12
    grade = '2023'  # current grade PE course.

    data = {
        'bklx_id': 0,
        'xkxnm': study_year,
        'xkxqm': term,
        'kklxdm': '05',
        'kspage': 1,
        'jspage': 10,
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
        'njdm_id': grade
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

        # next page
        data['kspage'] = int(data['jspage']) + 1
        data['jspage'] = int(data['jspage']) + 10
