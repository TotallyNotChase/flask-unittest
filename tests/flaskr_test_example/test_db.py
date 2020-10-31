import unittest
from typing import Iterator, Union

import sqlite3
import flask_unittest
from flask import Flask

from tests.flaskr.db import get_db
from tests.flaskr_test_example.conftest import _create_app

class TestDB(flask_unittest.AppTestCase):

    create_app = _create_app

    def test_get_close_db(self, app: Flask):
        with app.app_context():
            db = get_db()
            assert db is get_db()

        try:
            db.execute("SELECT 1")
        except sqlite3.ProgrammingError as e:
            self.assertIn("closed", str(e.args[0]))


if __name__ == '__main__':
    unittest.main()
