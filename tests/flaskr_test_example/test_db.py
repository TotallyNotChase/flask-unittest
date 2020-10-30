import unittest

import sqlite3
from flask import Flask

from tests.flaskr.db import get_db
from tests.flaskr_test_example.conftest import TestBase


class TestDB(TestBase):
    '''
    NOTE: This inherits TestBase which is an AppClientTestCase
    This test should ideally use an AppTestCase instead
    This is omitted here for brevity
    '''
    def test_get_close_db(self, app: Flask, _):
        with app.app_context():
            db = get_db()
            assert db is get_db()

        try:
            db.execute("SELECT 1")
        except sqlite3.ProgrammingError as e:
            self.assertIn("closed", str(e.args[0]))


if __name__ == '__main__':
    unittest.main()
