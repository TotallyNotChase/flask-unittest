import unittest


def suite():
    from example.tests.test_auth import TestAuth
    from example.tests.test_blog import TestBlog
    from example.tests.test_db import TestDB
    from example.tests.test_factory import TestConfig, TestHello
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAuth))
    suite.addTest(unittest.makeSuite(TestBlog))
    suite.addTest(unittest.makeSuite(TestDB))
    suite.addTest(unittest.makeSuite(TestConfig))
    suite.addTest(unittest.makeSuite(TestHello))
    return suite
