import unittest

import sqlite3
import flask_unittest
from flask import Flask

from example.flaskr.db import get_db
from example.tests.conftest import _create_app


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
