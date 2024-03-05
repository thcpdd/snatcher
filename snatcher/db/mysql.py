"""
备份表结构：mysqldump --opt -d select_course -u root -p > db.sql;
"""
from functools import lru_cache

from pymysql import Connection

from snatcher.conf import settings


@lru_cache()
def get_db_connection():
    return Connection(**settings.DATABASES['mysql'])


def execute_sql(sql: str, args: tuple = None):
    """
    执行sql语句
    :param sql:
    :param args:
    :return:
    """
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
    """
    创建一条选课数据
    :param username: 学号
    :param email: 邮箱
    :param course_name: 课程名称
    :param log_key: 日志关键字
    :return:
    """
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
    """
    创建一条选课失败数据
    :param username: 学号
    :param course_name: 课程名
    :param log_key: 日志key
    :param failed_reason: 失败原因
    :param port: 本次发送请求的端口
    :return:
    """
    sql = """
        INSERT INTO failed_data (`username`, `course_name`, `log_key`, `failed_reason`, `port`)
        VALUES (%s, %s, %s, %s, %s);
    """
    execute_sql(sql, args=(username, course_name, log_key, failed_reason, port))


def query_pc_course_id(course_no: str):
    """
    查询公选课课程id
    :param course_no: 课程号
    :return:
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
    查询体育课课程id
    :param grade: 年级 2022
    :param course_name: 部分课程名
    :return:
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
