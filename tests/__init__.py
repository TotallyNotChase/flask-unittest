import unittest

import flask_unittest


def livesuite():
    from tests.flask_live_test import TestSetup, TestIndex, TestAuth, TestBlog
    from tests.app_factory import build_app
    suite = flask_unittest.LiveTestSuite(build_app())
    suite.addTest(unittest.makeSuite(TestSetup))
    suite.addTest(unittest.makeSuite(TestIndex))
    suite.addTest(unittest.makeSuite(TestAuth))
    suite.addTest(unittest.makeSuite(TestBlog))
    return suite


def normalsuite():
    from tests import flask_app_test, flask_appclient_test, flask_client_test
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(flask_app_test.TestSetup))
    suite.addTest(unittest.makeSuite(flask_app_test.TestGlobals))
    suite.addTest(unittest.makeSuite(flask_appclient_test.TestSetup))
    suite.addTest(unittest.makeSuite(flask_appclient_test.TestGlobals))
    suite.addTest(unittest.makeSuite(flask_appclient_test.TestIndex))
    suite.addTest(unittest.makeSuite(flask_appclient_test.TestAuth))
    suite.addTest(unittest.makeSuite(flask_appclient_test.TestBlog))
    suite.addTest(unittest.makeSuite(flask_client_test.TestSetup))
    suite.addTest(unittest.makeSuite(flask_client_test.TestGlobals))
    suite.addTest(unittest.makeSuite(flask_client_test.TestIndex))
    suite.addTest(unittest.makeSuite(flask_client_test.TestAuth))
    suite.addTest(unittest.makeSuite(flask_client_test.TestBlog))
    return suite
