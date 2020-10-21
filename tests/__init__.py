import unittest
import flask_unittest

from tests.flask_app import create_app
from tests.flask_live_test import Foo

def suite():
    app = create_app()
    suite = flask_unittest.TestSuite(app)
    suite.addTest(unittest.makeSuite(Foo))
    return suite
