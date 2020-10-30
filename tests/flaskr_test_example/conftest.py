import os
import tempfile
from typing import Iterator, Union

from flask.testing import FlaskClient

import flask_unittest
from flask import Flask

from tests.flaskr import create_app
from tests.flaskr.db import get_db
from tests.flaskr.db import init_db

# read in SQL for populating test data
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


class TestBase(flask_unittest.AppClientTestCase):
    # The tests expect to use the session object - so set test_client to use cookies
    test_client_use_cookies = True

    def create_app(self) -> Union[Flask, Iterator[Flask]]:
        """Create and configure a new app instance for each test."""
        # create a temporary file to isolate the database for each test
        #db_fd, db_path = tempfile.mkstemp()
        # create the app with common test config
        app = create_app({"TESTING": True})

        # create the database and load test data
        with app.app_context():
            init_db()
            get_db().executescript(_data_sql)

        yield app

        # os.close(db_fd)
        # os.unlink(db_path)


class AuthActions(object):
    def __init__(self, client: FlaskClient):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post("/auth/login", data={"username": username, "password": password})

    def logout(self):
        return self._client.get("/auth/logout")
