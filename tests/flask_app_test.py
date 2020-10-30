import unittest

import flask_unittest
from flask import Flask
from flask.testing import FlaskClient
from flask.wrappers import Response
from flask.globals import g, session, request
from bs4 import BeautifulSoup

from tests.app_factory import build_app
from tests.mockdata import MockUser


class _TestBase(flask_unittest.AppTestCase):
    '''
    Base AppTestCase with helper functions used across other testcases

    NOTE: You absolutely don't need to have a TestBase class to write tests. It's just
    convenient in this case since the other testcases share the same methods/properties.
    As long as your testcase class extends flask_unittest.AppTestCase - it's fine
    '''
    def create_app(self) -> Flask:
        return build_app()

    ### Helper functions (not mandatory)

    def signup(self, client: FlaskClient, username: str, password: str):
        # Sign up with given credentials
        rv: Response = client.post(
            '/auth/register', data={'username': username, 'password': password}, follow_redirects=True
        )
        soup = BeautifulSoup(rv.data, 'html.parser')

        # Make sure the log in page is showing
        self.assertIn('Log In', soup.find('title').text)

    def login(self, client: FlaskClient, username: str, password: str):
        # Log in with given credentials
        rv: Response = client.post(
            '/auth/login', data={'username': username, 'password': password}, follow_redirects=True
        )
        soup = BeautifulSoup(rv.data, 'html.parser')

        # Make sure the Posts page is showing
        self.assertIn('Posts', soup.find('title').text)
        # Make sure login suceeded and the authorized links are showing
        self.assertTrue(soup.select('a[href="/auth/logout"]'))
        self.assertTrue(soup.select('a[href="/auth/delete"]'))

    def logout(self, client: FlaskClient):
        # Logs out of the signed in account
        rv: Response = client.get('/auth/logout', follow_redirects=True)
        soup = BeautifulSoup(rv.data, 'html.parser')

        # Make sure the Posts page is showing
        self.assertIn('Posts', soup.find('title').text)
        # Make sure logout suceeded and the non-authorized links are showing
        self.assertTrue(soup.select('a[href="/auth/register"]'))
        self.assertTrue(soup.select('a[href="/auth/login"]'))

    def delete(self, client: FlaskClient):
        # Deletes the signed in account
        rv: Response = client.post('/auth/delete', follow_redirects=True)
        soup = BeautifulSoup(rv.data, 'html.parser')

        # Make sure the Posts page is showing
        self.assertIn('Posts', soup.find('title').text)
        # Make sure delete suceeded and the non-authorized links are showing
        self.assertTrue(soup.select('a[href="/auth/register"]'))
        self.assertTrue(soup.select('a[href="/auth/login"]'))


class TestSetup(_TestBase):
    '''
    Make sure the testcases are set up correctly
    and all expected properties exist and are correct
    '''

    ### setUp and tearDown methods per testcase (not mandatory) - should have app as a parameter

    def setUp(self, app: Flask):
        # Make sure app is passed in correctly and has correct type
        self.assertTrue(app is not None)
        self.assertTrue(isinstance(app, Flask))

    def tearDown(self, app: Flask):
        # Make sure app is passed in correctly and has correct type
        self.assertTrue(app is not None)
        self.assertTrue(isinstance(app, Flask))

    ### Test methods (mandatory, obviously) - should have app as a parameter

    def test_ok(self, app: Flask):
        # Make sure app is passed in correctly and has correct type
        self.assertTrue(app is not None)
        self.assertTrue(isinstance(app, Flask))


class TestGlobals(_TestBase):
    '''
    Make sure the testcases' test methods can
    access the flask globals like request/session/g

    Also use the test_request_context as an example of practical use
    of the app object
    '''

    ### Test methods (mandatory, obviously) - should have app as a parameter

    def test_session(self, app: Flask):
        # Make sure the session global is accessible and has correct values
        with app.test_client() as client:
            self.signup(client, MockUser.username, MockUser.password)
            self.login(client, MockUser.username, MockUser.password)
            # Make sure the user_id is visible in session
            self.assertTrue('user_id' in session)
            self.delete(client)

    def test_request(self, app: Flask):
        # Make sure the request global is accessible and has correct values
        with app.test_client() as client:
            self.signup(client, MockUser.username, MockUser.password)
            self.login(client, MockUser.username, MockUser.password)
            # Make sure the request is at the correct endpoint
            self.assertEqual(request.endpoint, 'blog.index')
            self.delete(client)

    def test_g(self, app: Flask):
        # Make sure the g object is accessible and has correct values
        with app.test_client() as client:
            self.signup(client, MockUser.username, MockUser.password)
            self.login(client, MockUser.username, MockUser.password)
            # Make sure the g object has the correct user assigned
            self.assertEqual(g.user['username'], MockUser.username)
            self.delete(client)

    def test_request_context(self, app: Flask):
        # Demonstration of using the test_request_context
        with app.test_request_context('/1/update'):
            self.assertEqual(request.endpoint, 'blog.update')


if __name__ == '__main__':
    unittest.main()
