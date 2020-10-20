import unittest
import flask_unittest

from flask_app import create_app

class Foo(flask_unittest.TestCase):
    def test_1_pog(self):
        print(self.server_url)


if __name__ == '__main__':
    app = create_app()
    runner = unittest.TextTestRunner()
    suite = flask_unittest.TestSuite(app)
    suite.addTest(Foo('test_1_pog'))
    runner.run(suite)
