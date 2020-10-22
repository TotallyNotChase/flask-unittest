import flask_unittest

from tests.app_factory import app

class TestSetup(flask_unittest.LiveTestCase):

    def test_setup(self):
        # Make sure the testcase is set up all correctly
        # i.e make sure the properties were injected
        self.assertTrue(self.server_url is not None)
        self.assertTrue(self.app is not None)

    def test_values(self):
        # Make sure the injected values are correct
        self.assertEqual(self.app, app)
        self.assertEqual(self.server_url, f'http://127.0.0.1:{app.config.get("PORT", 5000)}')
