import sqlite3
import threading
from contextlib import closing

import pytest
import requests

from tlsod_authorize.webserver import TlsodHTTPServer, WebRequestHandler


@pytest.fixture(scope="session")
def db_path():
    # use an im-memory DB for testing
    return ":memory:"


@pytest.fixture(scope="session")
def db(db_path):
    """
    Get DB instance
    NB: the webserver may be running in a different thread
    """
    with closing(sqlite3.connect(db_path, check_same_thread=False)) as db:
        yield db


@pytest.fixture(scope="session")
def create_tables(db):
    """
    Create table structure
    """
    with closing(db.cursor()) as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS domains (domain text)""")
        yield db


@pytest.fixture(scope="session", autouse=True)
def populate_db(create_tables, db):
    """
    Add test records
    """
    with closing(db.cursor()) as cursor:
        cursor.execute("""INSERT INTO domains (domain) VALUES ('test.com')""")
        db.commit()


@pytest.fixture(scope="session")
def webserver(db):
    """
    Get webserver instance
    Request port 0 to assign available port automatically
    """
    server = TlsodHTTPServer(db, ("", 0), WebRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    yield server

    server.shutdown()


@pytest.fixture(scope="session")
def session(webserver):
    with requests.Session() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def url(webserver):
    return f"http://localhost:{webserver.server_port}"
