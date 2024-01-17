import logging
import sqlite3
from contextlib import closing

logger = logging.getLogger(__name__)


def create_db(db_path: str):
    logger.debug("Create SQLite DB and tables")
    with closing(sqlite3.connect(db_path)) as con:
        with closing(con.cursor()) as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS domains (domain text)"""
            )
