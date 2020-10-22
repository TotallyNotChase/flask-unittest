import unittest

import flask_unittest

from tests.flask_live_test import TestSetup
from tests.app_factory import app

def suite():
    suite = flask_unittest.LiveTestSuite(app)
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
