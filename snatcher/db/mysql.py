"""
This module provide any querier for controlling mysql.
Every querier just like a simple ORM.

back up db struct: mysqldump --opt -d select_course -u root -p > db.sql;
"""
from functools import lru_cache

from pymysql.err import MySQLError
from pymysql import Connection
from pymysql.cursors import Cursor, DictCursor

from snatcher.conf import settings


study_year = settings.SELECT_COURSE_YEAR
term = settings.TERM
period = settings.PERIOD


def get_db_connection():
    return Connection(**settings.DATABASES['mysql'])


# def execute_sql(sql: str, args: tuple = None, cursor: Type[Cursor] = None):
#     db = get_db_connection()
#     cursor = db.cursor(cursor=cursor)
#     cursor.execute(sql, args)
#     db.commit()
#     return cursor
#
#
# def create_selected_data(
#     username: str,
#     email: str,
#     course_name: str,
#     log_key: str
# ):
#     """create a select data."""
#     sql = """
#         INSERT INTO selected_course_data (`username`, `email`, `course_name`, `log_key`)
#         VALUES (%s, %s, %s, %s);
#     """
#     execute_sql(sql, args=(username, email, course_name, log_key))
#
#
# def create_failed_data(
#     username: str,
#     course_name: str,
#     log_key: str,
#     failed_reason: str,
#     port: int
# ):
#     """create a failed data."""
#     sql = """
#         INSERT INTO failed_data (`username`, `course_name`, `log_key`, `failed_reason`, `port`)
#         VALUES (%s, %s, %s, %s, %s);
#     """
#     execute_sql(sql, args=(username, course_name, log_key, failed_reason, port))
#
#
# @lru_cache()
# def query_all_pc_course(page=1, page_size=10):
#     start = (page - 1) * 10
#     page_size = page_size
#     sql = """
#         SELECT * FROM pc
#         WHERE `study_year`=%s and `term`=%s and `period`=%s
#         ORDER BY `id`
#         LIMIT %s, %s;
#     """
#     cursor = execute_sql(sql, args=(study_year, term, period, start, page_size),
#                          cursor=DictCursor)
#     return cursor.fetchall()
#
#
# @lru_cache()
# def query_all_pe_course(page=1, page_size=10):
#     start = (page - 1) * 10
#     page_size = page_size
#     sql = """
#         SELECT * FROM pe
#         WHERE `study_year`=%s and `term`=%s
#         ORDER BY `id`
#         LIMIT %s, %s;
#     """
#     cursor = execute_sql(sql, args=(study_year, term, start, page_size), cursor=DictCursor)
#     return cursor.fetchall()
#
#
# @lru_cache()
# def query_pc_course_count() -> int:
#     sql = """
#         SELECT COUNT(`id`) FROM pc
#         WHERE `study_year`=%s and `term`=%s and `period`=%s;
#     """
#     cursor = execute_sql(sql, args=(study_year, term, period))
#     return cursor.fetchone()[0]
#
#
# @lru_cache()
# def query_pe_course_count() -> int:
#     sql = """
#         SELECT COUNT(`id`) FROM pe
#         WHERE `study_year`=%s and `term`=%s;
#     """
#     cursor = execute_sql(sql, args=(study_year, term))
#     return cursor.fetchone()[0]
#
#
# def query_pe_course(condition):
#     sql = """
#     SELECT `id`, `course_id`, `course_name`, `grade` FROM pe
#     WHERE `study_year`=%s and `term`=%s and `course_name` like %s;
#     """
#     cursor = execute_sql(sql, args=(study_year, term, f'%{condition}%'), cursor=DictCursor)
#     return cursor.fetchall()
#
#
# def query_pc_course(condition):
#     sql = """
#     SELECT `id`, `course_id`, `course_name`, `course_no` FROM pc
#     WHERE `study_year`=%s and `term`=%s and `period`=%s and `course_name` like %s;
#     """
#     cursor = execute_sql(sql, args=(study_year, term, period, f'%{condition}%'), cursor=DictCursor)
#     return cursor.fetchall()
#
#
# def generate_verify_code(username: str):
#     """Creating a verify code into database and return it."""
#     code = str(int(time())) + str(randint(0, 9))
#     verify_code = md5(code.encode()).hexdigest()
#     sql = """
#         INSERT INTO verify_codes (`verify_code`, `username`)
#         VALUES (%s, %s);
#     """
#     execute_sql(sql, args=(verify_code, username))
#     return verify_code
#
#
# def check_verify_code(username: str, verify_code: str) -> tuple:
#     """Check if the verify code is valid."""
#     sql = """
#         SELECT `is_used` FROM verify_codes
#         WHERE `verify_code`=%s and `username`=%s;
#     """
#     cursor = execute_sql(sql, args=(verify_code, username))
#     return cursor.fetchone()
#
#
# def mark_verify_code_is_used(username: str, verify_code: str):
#     """Mark the verify code as used."""
#     sql = """
#         UPDATE verify_codes
#         SET `is_used`=1
#         WHERE `verify_code`=%s and `username`=%s;
#     """
#     execute_sql(sql, args=(verify_code, username))
#
#
# def query_all_selected_data(page=1, page_size=10):
#     start = (page - 1) * 10
#     page_size = page_size
#     sql = """
#         SELECT `id`, `username`, `email`, `course_name`, `log_key`, `created_at` FROM selected_course_data
#         ORDER BY `id` DESC
#         LIMIT %s, %s;
#     """
#     cursor = execute_sql(sql, args=(start, page_size), cursor=DictCursor)
#     return cursor.fetchall()
#
#
# def query_selected_data_count() -> int:
#     sql = """SELECT COUNT(`id`) FROM selected_course_data;"""
#     cursor = execute_sql(sql)
#     return cursor.fetchone()[0]
#
#
# def query_failed_data_count() -> int:
#     sql = """SELECT COUNT(`id`) FROM failed_data;"""
#     cursor = execute_sql(sql)
#     return cursor.fetchone()[0]
#
#
# def query_failed_data(page=1, page_size=10):
#     start = (page - 1) * 10
#     page_size = page_size
#     sql = """
#         SELECT `id`, `username`, `port`, `course_name`, `log_key`, `failed_reason`, `created_at` FROM failed_data
#         ORDER BY `id` DESC
#         LIMIT %s, %s;
#     """
#     cursor = execute_sql(sql, args=(start, page_size), cursor=DictCursor)
#     return cursor.fetchall()
#
#
# def query_all_verify_codes(page=1, page_size=10):
#     start = (page - 1) * 10
#     page_size = page_size
#     sql = "SELECT * FROM verify_codes LIMIT %s,%s;"
#     cursor = execute_sql(sql, args=(start, page_size), cursor=DictCursor)
#     return cursor.fetchall()
#
#
# def query_verify_code_count() -> int:
#     sql = "SELECT COUNT(`id`) FROM verify_codes;"
#     cursor = execute_sql(sql)
#     return cursor.fetchone()[0]


class SQLQuerier:
    """
    A base class for all SQL querier.

    `table`:
        You must override the class variable of `table` in your subclass,
        it appoints a specific database table.

    `condition`:
        It will attach in `pagination_query` and `count` method to filter data.
        And it can be null.
    """
    table = None  # Overriding in your subclass !
    condition = ""

    def __init__(self):
        self._connection = None

    def execute(
        self,
        sql: str,
        args: tuple = None,
        cursor: type[Cursor] = None
    ) -> Cursor | None:
        if self._connection is None:
            self._connection = get_db_connection()
        cursor = self._connection.cursor(cursor=cursor)
        try:
            cursor.execute(sql, args)
            self._connection.commit()
        except MySQLError:
            self._connection.rollback()
            return None
        else:
            return cursor

    @lru_cache()
    def parse_query_result(
        self,
        sql: str,
        args: tuple = None,
        dict_cursor: bool = True,
        many: bool = True
    ):
        cursor = self.execute(sql, args, DictCursor if dict_cursor else None)
        if many:
            if cursor is None:
                return []
            return cursor.fetchall()
        else:
            if cursor is None:
                return None
            return cursor.fetchone()

    @lru_cache()
    def parse_count_result(
        self,
        sql: str,
        args: tuple = None
    ) -> int:
        cursor = self.execute(sql, args)
        if cursor is None:
            return 0
        return cursor.fetchone()[0]

    def pagination_query(
        self,
        page: int,
        page_size: int = 10,
        dict_cursor: bool = True,
        fields: tuple | None = None,
    ):
        if page <= 0:
            page = 1
        current_page = (page - 1) * 10
        if not fields:
            _fields = "*"
        else:
            _fields = ", ".join(fields)
        _sql = "SELECT " + _fields + " FROM {} ".format(self.table)
        _sub_sql = "WHERE `id` >= (SELECT `id` FROM {} {} ORDER BY `id` LIMIT %s, 1) " \
                   "LIMIT %s;".format(self.table, self.condition)
        return self.parse_query_result(_sql + _sub_sql, (current_page, page_size), dict_cursor)

    def count(self) -> int:
        _sql = "SELECT COUNT(`id`) FROM " + self.table + ' ' + self.condition
        return self.parse_count_result(_sql)


class PCQuerier(SQLQuerier):
    table = 'pc'
    condition = "WHERE study_year={} AND term={} AND period={}".format(study_year, term, period)

    def insert(self, *values):
        _sql = """INSERT INTO pc 
            (`course_name`, `course_id`, `course_no`, `study_year`, `term`, `period`)
            VALUES (%s, %s ,%s, %s, %s, %s);
        """
        self.execute(_sql, values)

    def like_query(self, course_name: str):
        _sql = "SELECT `id`, `course_id`, `course_name`, `course_no` FROM pc " + self.condition
        _sub_sql = ' AND `course_name` like %s'
        return self.parse_query_result(_sql + _sub_sql, (f'%{course_name}%',))


class PEQuerier(SQLQuerier):
    table = 'pe'
    condition = "WHERE study_year={} AND term={}".format(study_year, term)

    def insert(self, *values):
        _sql = """INSERT INTO pe 
            (`course_name`, `course_id`, `grade`, `study_year`, `term`)
            VALUES (%s,%s,%s,%s,%s);
        """
        self.execute(_sql, values)

    def like_query(self, course_name: str):
        _sql = "SELECT `id`, `course_id`, `course_name`, `grade` FROM pe " + self.condition
        _sub_sql = ' AND `course_name` like %s'
        return self.parse_query_result(_sql + _sub_sql, (f'%{course_name}%',))


class FailedDataQuerier(SQLQuerier):
    table = 'failed_data'

    def insert(self, *values):
        _sql = """INSERT INTO failed_data 
            (`username`, `course_name`, `log_key`, `failed_reason`, `port`)
            VALUES (%s,%s,%s,%s,%s);
        """
        self.execute(_sql, values)


class SelectedCourseDataQuerier(SQLQuerier):
    table = "selected_course_data"

    def insert(self, *values):
        _sql = """
            INSERT INTO selected_course_data (`username`, `email`, `course_name`, `log_key`)
            VALUES (%s, %s, %s, %s);
        """
        self.execute(_sql, values)


class VerifyCodesQuerier(SQLQuerier):
    table = "verify_codes"

    def insert(self, username: str):
        from time import time
        from random import randint
        from hashlib import md5

        code = str(int(time())) + str(randint(0, 9))
        verify_code = md5(code.encode()).hexdigest()
        _sql = """
            INSERT INTO verify_codes (`verify_code`, `username`)
            VALUES (%s, %s);
        """
        self.execute(_sql, (verify_code, username))

    def query(self, username: str, verify_code: str):
        _sql = "SELECT `is_used` FROM verify_codes WHERE `verify_code`=%s AND `username`=%s;"
        return self.parse_query_result(_sql, (verify_code, username), many=False, dict_cursor=False)

    def update(self, username: str, verify_code: str):
        _sql = "UPDATE verify_codes SET `is_used`=1 WHERE `verify_code`=%s AND `username`=%s;"
        self.execute(_sql, (verify_code, username))


########################################
#  Importing querier object directly.  #
########################################
pc_querier = PCQuerier()
pe_querier = PEQuerier()
fd_querier = FailedDataQuerier()
scd_querier = SelectedCourseDataQuerier()
vc_querier = VerifyCodesQuerier()
