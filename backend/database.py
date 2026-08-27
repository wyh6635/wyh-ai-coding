import pymysql
from contextlib import contextmanager
from config import DB_CONFIG


@contextmanager
def get_connection():
    conn = None
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor
        )
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def query_one(sql: str, params: tuple = None):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()


def query_list(sql: str, params: tuple = None):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


def execute(sql: str, params: tuple = None):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            result = cursor.execute(sql, params)
            return result