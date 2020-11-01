import unittest

import flask_unittest
from flask.testing import FlaskClient

from example.flaskr import create_app


class TestConfig(unittest.TestCase):
    def test_config(self):
        """Test create_app without passing test config."""
        self.assertFalse(create_app().testing)
        self.assertTrue(create_app({"TESTING": True}).testing)


class TestHello(flask_unittest.ClientTestCase):
    app = create_app({"TESTING": True})

    def test_hello(self, client: FlaskClient):
        response = client.get("/hello")
        self.assertResponseEqual(response, b"Hello, World!")


if __name__ == '__main__':
    unittest.main()
