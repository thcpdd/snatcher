"""
This module provide some function for controlling mysql.

back up db struct: mysqldump --opt -d select_course -u root -p > db.sql;
"""
from time import time
from random import randint
from typing import Type
from functools import lru_cache
from hashlib import md5

from pymysql import Connection
from pymysql.cursors import Cursor, DictCursor

from snatcher.conf import settings


def get_db_connection():
    return Connection(**settings.DATABASES['mysql'])


def execute_sql(sql: str, args: tuple = None, cursor: Type[Cursor] = None):
    db = get_db_connection()
    cursor = db.cursor(cursor=cursor)
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


@lru_cache()
def query_pc_course_id(course_no: str):
    """
    query PC id
    :param course_no: the course number
    :return: (course_id, course_name)
    """
    sql = """
        SELECT `course_id`, `course_name` FROM public_choice_course 
        WHERE `study_year`=%s and `term`=%s and `course_no`=%s;
    """
    cursor = execute_sql(sql, args=(settings.SELECT_COURSE_YEAR, settings.TERM, course_no))
    data = cursor.fetchone()
    if not data:
        return '', ''
    return data


@lru_cache()
def query_pe_course_id(grade: int, course_name: str):
    """
    query pe course id
    :param grade: grade 2022
    :param course_name: the part of course name
    :return: (course_id, course_name)
    """
    sql = """
        SELECT `course_id`, `course_name` FROM physical_education_course 
        WHERE `study_year`=%s and `term`=%s and `grade`=%s and `course_name` like %s;
    """
    cursor = execute_sql(sql, args=(settings.SELECT_COURSE_YEAR, settings.TERM, grade, f'%{course_name}%'))
    data = cursor.fetchone()
    if not data:
        return '', ''
    return data


@lru_cache()
def query_all_pc_course(page=1, page_size=10):
    start = (page - 1) * 10
    page_size = page_size
    sql = """
        SELECT * FROM public_choice_course
        WHERE `study_year`=%s and `term`=%s
        ORDER BY `id` 
        LIMIT %s, %s;
    """
    cursor = execute_sql(sql, args=(settings.SELECT_COURSE_YEAR, settings.TERM, start, page_size), cursor=DictCursor)
    return cursor.fetchall()


@lru_cache()
def query_all_pe_course(page=1, page_size=10):
    start = (page - 1) * 10
    page_size = page_size
    sql = """
        SELECT * FROM physical_education_course
        WHERE `study_year`=%s and `term`=%s
        ORDER BY `id` 
        LIMIT %s, %s;
    """
    cursor = execute_sql(sql, args=(settings.SELECT_COURSE_YEAR, settings.TERM, start, page_size), cursor=DictCursor)
    return cursor.fetchall()


@lru_cache()
def query_pc_course_count() -> int:
    sql = """
        SELECT COUNT(`id`) FROM public_choice_course
        WHERE `study_year`=%s and `term`=%s;
    """
    cursor = execute_sql(sql, args=(settings.SELECT_COURSE_YEAR, settings.TERM))
    return cursor.fetchone()[0]


@lru_cache()
def query_pe_course_count() -> int:
    sql = """
        SELECT COUNT(`id`) FROM physical_education_course
        WHERE `study_year`=%s and `term`=%s;
    """
    cursor = execute_sql(sql, args=(settings.SELECT_COURSE_YEAR, settings.TERM))
    return cursor.fetchone()[0]


def query_pe_course(condition):
    sql = """
    SELECT `id`, `course_id`, `course_name`, `grade` FROM physical_education_course
    WHERE `study_year`=%s and `term`=%s and `course_name` like %s;
    """
    cursor = execute_sql(sql, args=(settings.SELECT_COURSE_YEAR, settings.TERM, f'%{condition}%'), cursor=DictCursor)
    return cursor.fetchall()


def query_pc_course(condition):
    sql = """
    SELECT `id`, `course_id`, `course_name`, `course_no` FROM public_choice_course
    WHERE `study_year`=%s and `term`=%s and `course_name` like %s;
    """
    cursor = execute_sql(sql, args=(settings.SELECT_COURSE_YEAR, settings.TERM, f'%{condition}%'), cursor=DictCursor)
    return cursor.fetchall()


def generate_verify_code(username: str):
    """Creating a verify code into database and return it."""
    code = str(int(time())) + str(randint(0, 9))
    verify_code = md5(code.encode()).hexdigest()
    sql = """
        INSERT INTO verify_codes (`verify_code`, `username`)
        VALUES (%s, %s);
    """
    execute_sql(sql, args=(verify_code, username))
    return verify_code


def check_verify_code(username: str, verify_code: str) -> tuple:
    """Check if the verify code is valid."""
    sql = """
        SELECT `is_used` FROM verify_codes
        WHERE `verify_code`=%s and `username`=%s;
    """
    cursor = execute_sql(sql, args=(verify_code, username))
    return cursor.fetchone()


def mark_verify_code_is_used(username: str, verify_code: str):
    """Mark the verify code as used."""
    sql = """
        UPDATE verify_codes
        SET `is_used`=1
        WHERE `verify_code`=%s and `username`=%s;
    """
    execute_sql(sql, args=(verify_code, username))


def query_all_selected_data(page=1, page_size=10):
    start = (page - 1) * 10
    page_size = page_size
    sql = """
        SELECT `id`, `username`, `email`, `course_name`, `log_key`, `created_at` FROM selected_course_data
        ORDER BY `id` DESC
        LIMIT %s, %s;
    """
    cursor = execute_sql(sql, args=(start, page_size), cursor=DictCursor)
    return cursor.fetchall()


def query_selected_data_count() -> int:
    sql = """SELECT COUNT(`id`) FROM selected_course_data;"""
    cursor = execute_sql(sql)
    return cursor.fetchone()[0]


def query_failed_data_count() -> int:
    sql = """SELECT COUNT(`id`) FROM failed_data;"""
    cursor = execute_sql(sql)
    return cursor.fetchone()[0]


def query_failed_data(page=1, page_size=10):
    start = (page - 1) * 10
    page_size = page_size
    sql = """
        SELECT `id`, `username`, `port`, `course_name`, `log_key`, `failed_reason`, `created_at` FROM failed_data
        ORDER BY `id` DESC
        LIMIT %s, %s;
    """
    cursor = execute_sql(sql, args=(start, page_size), cursor=DictCursor)
    return cursor.fetchall()


def query_all_verify_codes(page=1, page_size=10):
    start = (page - 1) * 10
    page_size = page_size
    sql = "SELECT * FROM verify_codes LIMIT %s,%s;"
    cursor = execute_sql(sql, args=(start, page_size), cursor=DictCursor)
    return cursor.fetchall()


def query_verify_code_count() -> int:
    sql = "SELECT COUNT(`id`) FROM verify_codes;"
    cursor = execute_sql(sql)
    return cursor.fetchone()[0]


if __name__ == '__main__':
    # for data in query_all_verify_codes():
    #     print(data)
    print(type(query_failed_data_count()))
