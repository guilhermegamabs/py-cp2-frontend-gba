import logging
from contextlib import contextmanager
from typing import Iterator

import pymysql
from pymysql.cursors import DictCursor

from core.config.settings import settings

logger = logging.getLogger(__name__)


@contextmanager
def connection() -> Iterator[pymysql.connections.Connection]:
    conn = pymysql.connect(
        host=settings.database.host,
        port=settings.database.port,
        user=settings.database.user,
        password=settings.database.password,
        database=settings.database.database,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check_connection() -> None:
    try:
        with connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM sensor_tb_request_processing")
                total = cursor.fetchone()["total"]
        logger.info(
            "Conectado ao MySQL %s:%s/%s — %s registros de processamento.",
            settings.database.host, settings.database.port, settings.database.database, total,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Não foi possível acessar `{settings.database.database}`: {exc}. "
            "Aplique o schema antes de subir a API: mysql -u root -proot < db/V1__schema.sql"
        ) from exc
