import os
import tempfile
from typing import Iterator, Union
from flask.globals import g

from flask.testing import FlaskClient

import flask_unittest
from flask import Flask

from tests.flaskr import create_app
from tests.flaskr.db import close_db, get_db
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
        db_fd, db_path = tempfile.mkstemp()
        # create the app with common test config
        app = create_app({"TESTING": True, "DATABASE": db_path})

        # create the database and load test data
        with app.app_context():
            init_db()
            get_db().executescript(_data_sql)

            # Yield the app
            '''
            This can be outside the `with` block too, but we need to 
            call `close_db` before exiting current context
            Otherwise windows will have trouble removing the temp file
            that doesn't happen on unices though, which is nice
            '''
            yield app

            ## Close the db
            close_db()
        
        ## Cleanup temp file
        os.close(db_fd)
        os.remove(db_path)


class AuthActions(object):
    def __init__(self, client: FlaskClient):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post("/auth/login", data={"username": username, "password": password})

    def logout(self):
        return self._client.get("/auth/logout")
