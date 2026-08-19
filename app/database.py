import mysql.connector
from mysql.connector import pooling, Error
import os
from dotenv import load_dotenv
load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "dalal_street_pro"),
    "ssl_disabled": os.getenv("DB_SSL_DISABLED", "false").lower() == "true",
}
_pool = pooling.MySQLConnectionPool(pool_name="dalal_pool", pool_size=10, **DB_CONFIG)

def query(sql: str, params: tuple = (), fetch: bool = False, return_lastrowid: bool = False):
    conn = _pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        if fetch:
            result = cursor.fetchall()
            return result
        conn.commit()
        if return_lastrowid:
            return cursor.lastrowid
        return cursor.rowcount
    except Error as e:
        conn.rollback()
        raise RuntimeError(f"DB Error: {e}") from e
    finally:
        cursor.close()
        conn.close()
