"""
Módulo de conexión y gestión de transacciones para PostgreSQL.
"""
import logging
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

_connection_pool = None

def get_connection_pool():
    """Inicializa y retorna el pool de conexiones a PostgreSQL."""
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=15,
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            logger.info("Pool de conexiones a PostgreSQL inicializado con éxito.")
        except Exception as e:
            logger.error(f"Error al inicializar pool de conexiones PostgreSQL: {e}")
            raise e
    return _connection_pool

@contextmanager
def get_db_connection():
    """Context manager para obtener una conexión del pool."""
    p = get_connection_pool()
    conn = p.getconn()
    try:
        yield conn
    finally:
        p.putconn(conn)

@contextmanager
def get_db_cursor(commit=False, dict_cursor=True):
    """Context manager para obtener un cursor con soporte opcional para diccionarios y auto-commit."""
    with get_db_connection() as conn:
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error en transacción PostgreSQL: {e}")
            raise e
        finally:
            cursor.close()

def execute_query(sql: str, params: tuple = None, fetch: str = "all", commit: bool = False):
    """
    Función utilitaria de ejecución de consultas.
    fetch: 'all', 'one', 'val', 'none'
    """
    with get_db_cursor(commit=commit, dict_cursor=True) as cursor:
        cursor.execute(sql, params or ())
        if fetch == "all":
            return cursor.fetchall()
        elif fetch == "one":
            return cursor.fetchone()
        elif fetch == "val":
            row = cursor.fetchone()
            return list(row.values())[0] if row else None
        return None
