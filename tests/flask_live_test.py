import flask_unittest

class Foo(flask_unittest.TestCase):
    def test_1_pog(self):
        print(self.server_url)
