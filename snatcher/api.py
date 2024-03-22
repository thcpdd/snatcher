"""
Some interfaces of this project to start.
    1. The `physical_education` function:
        A interface to send a 'PE' select course task to celery task queue.

    2. The `public_choice` function:
        A interface to send a 'PC' select course task to celery task queue.

    3. The `update_data` function:
        Updating course information to mysql.
        If the argument `grade` is null, all data will write to `public_choice_course` table.
        Otherwise, all data will write to `physical_education_course` table.

    4. The `update_pc_data` function:
        Updating the 'PC' course data to database.

    5. The `update_pe_data` function:
        Updating the 'PE' course data to database.
"""
import requests
from requests.exceptions import JSONDecodeError

from .conf import settings
from .tasks import select_course
from .db.mysql import get_db_connection


def physical_education(
    goals: list[tuple[str, str]],
    **users
):
    """
    send a PE select course task.
    :param goals: [(course_name, course_id),...]
    :param users: It must contain: username, password, email, verify_code
    :return:
    """
    select_course.delay(goals, 'PE', **users)


def public_choice(
    goals: list[tuple[str, str]],
    **users
):
    """
    send a PC select course task.
    :param goals: [(course_name, course_id),...]
    :param users: It must contain: username, password, email, verify_code
    :return:
    """
    select_course.delay(goals, 'PC', **users)


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
        'Cookie': 'JSESSIONID=94258A739E2D283AF575FDB08642EB48; route=3d51944d5f53d489f356b638f274e4fb'
    }
    if grade is not None:
        data['njdm_id'] = grade  # add a must field
        data['kklxdm'] = '05'
        sql = """INSERT INTO physical_education_course 
            (`course_name`, `course_id`, `grade`, `study_year`, `term`)
            VALUES (%s,%s,%s,%s,%s);
        """
    else:
        data['kklxdm'] = '10'
        sql = """INSERT INTO public_choice_course 
            (`course_name`, `course_id`, `course_no`, `study_year`, `term`)
            VALUES (%s,%s,%s,%s,%s);
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
                cursor.execute(sql, (json_data['kcmc'], json_data['kch_id'], json_data['kch'], study_year, term))
        db.commit()

        # next page
        data['kspage'] = data['jspage'] + 1
        data['jspage'] += 10


def update_pc_data():
    update_data()


def update_pe_data(grade: str):
    update_data(grade)
