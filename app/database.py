import mysql.connector
from mysql.connector import pooling, Error
import os
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "dalal_street_pro"),
}
_pool = pooling.MySQLConnectionPool(pool_name="dalal_pool", pool_size=10, **DB_CONFIG)

def query(sql: str, params: tuple = (), fetch: bool = False):
    conn = _pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return cursor.rowcount
    except Error as e:
        conn.rollback()
        raise RuntimeError(f"DB Error: {e}") from e
    finally:
        cursor.close()
        conn.close()
