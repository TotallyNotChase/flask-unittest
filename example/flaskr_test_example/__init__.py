import unittest


def suite():
    from example.flaskr_test_example.test_auth import TestAuth
    from example.flaskr_test_example.test_blog import TestBlog
    from example.flaskr_test_example.test_db import TestDB
    from example.flaskr_test_example.test_factory import TestConfig, TestHello
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAuth))
    suite.addTest(unittest.makeSuite(TestBlog))
    suite.addTest(unittest.makeSuite(TestDB))
    suite.addTest(unittest.makeSuite(TestConfig))
    suite.addTest(unittest.makeSuite(TestHello))
    return suite