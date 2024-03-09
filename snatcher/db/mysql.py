"""
This module provide some function for controlling mysql.

back up db struct: mysqldump --opt -d select_course -u root -p > db.sql;
"""
from functools import lru_cache

from pymysql import Connection

from snatcher.conf import settings


@lru_cache()
def get_db_connection():
    return Connection(**settings.DATABASES['mysql'])


def execute_sql(sql: str, args: tuple = None):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(sql, args)
    db.commit()
    return cursor


def create_selected_data(
    username: str,
    email: str,
    course_name: str,
    log_key: str
):
    """create a select data."""
    sql = """
        INSERT INTO selected_course_data (`username`, `email`, `course_name`, `log_key`)
        VALUES (%s, %s, %s, %s);
    """
    execute_sql(sql, args=(username, email, course_name, log_key))


def create_failed_data(
    username: str,
    course_name: str,
    log_key: str,
    failed_reason: str,
    port: int
):
    """create a failed data."""
    sql = """
        INSERT INTO failed_data (`username`, `course_name`, `log_key`, `failed_reason`, `port`)
        VALUES (%s, %s, %s, %s, %s);
    """
    execute_sql(sql, args=(username, course_name, log_key, failed_reason, port))


def query_pc_course_id(course_no: str):
    """
    query PC id
    :param course_no: the course number
    :return: (course_id, course_name)
    """
    sql = """
        SELECT `course_id`, `course_name` FROM public_choice_course 
        WHERE `course_no`=%s;
    """
    cursor = execute_sql(sql, args=(course_no,))
    data = cursor.fetchone()
    if not data:
        return '', ''
    return data


def query_pe_course_id(grade: int, course_name: str):
    """
    query pe course id
    :param grade: grade 2022
    :param course_name: the part of course name
    :return: (course_id, course_name)
    """
    sql = """
        SELECT `course_id`, `course_name` FROM physical_education_course 
        WHERE `grade`=%s and `course_name` like %s;
    """
    cursor = execute_sql(sql, args=(grade, f'%{course_name}%'))
    data = cursor.fetchone()
    if not data:
        return '', ''
    return data
