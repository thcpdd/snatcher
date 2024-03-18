"""
This module provide some function for controlling mysql.

back up db struct: mysqldump --opt -d select_course -u root -p > db.sql;
"""
from typing import Type
from functools import lru_cache

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
        SELECT `id`, `course_id`, `course_name`, `course_no` FROM public_choice_course
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
        SELECT `id`, `course_id`, `course_name`, `grade` FROM physical_education_course
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
