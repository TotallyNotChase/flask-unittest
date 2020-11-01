import unittest

import flask_unittest
from flask.testing import FlaskClient
from flask.wrappers import Response
from flask.globals import g, session, request
from bs4 import BeautifulSoup
from bs4.element import PageElement

from tests.app_factory import build_app
from tests.mockdata import MockUser, MockPosts


class TestBase(flask_unittest.ClientTestCase):
    '''
    Base ClientTestCase with helper functions used across other testcases

    Also sets up common properties

    Note this class should only be extended, it does not have any tests
    Nor does it set up app - that's per testcase

    Though if you want to use the same app across multiple testcases instead
    calling `build_app` in each of them, you can put set `app` here and it'll be
    present in the classes that inherit this class

    Alternately, you can use a global variable that stores the result of `build_app()`
    and just assign that to each testcase, essentially using the same app instance
    for all of them

    NOTE: You absolutely don't need to have a TestBase class to write tests. It's just
    convenient in this case since the other testcases share the same methods/properties.
    As long as your testcase class extends flask_unittest.ClientTestCase - it's fine
    '''

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


class TestSetup(TestBase):
    '''
    Make sure the testcases are set up correctly
    and all expected properties exist and are correct
    '''
    # Assign the flask app
    app = build_app()

    ### setUp and tearDown methods per testcase (not mandatory) - should have client as a parameter

    def setUp(self, client: FlaskClient):
        # Make sure client is passed in correctly and has correct type
        self.assertTrue(client is not None)
        self.assertTrue(isinstance(client, FlaskClient))

    def tearDown(self, client: FlaskClient):
        # Make sure client is passed in correctly and has correct type
        self.assertTrue(client is not None)
        self.assertTrue(isinstance(client, FlaskClient))

    ### Test methods (mandatory, obviously) - should have client as a parameter

    def test_setup(self, client: FlaskClient):
        # Make sure client is passed in correctly and has correct type
        self.assertTrue(client is not None)
        self.assertTrue(isinstance(client, FlaskClient))


class TestGlobals(TestBase):
    '''
    Make sure the testcases' test methods can
    access the flask globals like request/session/g
    '''
    # Assign the flask app
    app = build_app()

    def test_session(self, client: FlaskClient):
        # Make sure the session global is accessible and has correct values
        self.signup(client, MockUser.username, MockUser.password)
        self.login(client, MockUser.username, MockUser.password)
        # Make sure the user_id is visible in session
        self.assertTrue('user_id' in session)
        self.delete(client)

    def test_request(self, client: FlaskClient):
        # Make sure the request global is accessible and has correct values
        self.signup(client, MockUser.username, MockUser.password)
        self.login(client, MockUser.username, MockUser.password)
        # Make sure the request is at the correct endpoint
        self.assertEqual(request.endpoint, 'blog.index')
        self.delete(client)

    def test_g(self, client: FlaskClient):
        self.signup(client, MockUser.username, MockUser.password)
        self.login(client, MockUser.username, MockUser.password)
        # Make sure the g object is accessible and has the correct user assigned to it
        self.assertEqual(g.user['username'], MockUser.username)
        self.delete(client)


class TestIndex(TestBase):
    '''
    Test the index page of the app
    '''
    # Assign the flask app
    app = build_app()

    ### Test methods (mandatory, obviously) - should have client as a parameter

    def test_presence_of_links(self, client: FlaskClient):
        # Make sure the register and login links are present in index page
        rv: Response = client.get('/')
        soup = BeautifulSoup(rv.data, 'html.parser')
        self.assertTrue(soup.select('a[href="/auth/register"]'))
        self.assertTrue(soup.select('a[href="/auth/login"]'))


class TestAuth(TestBase):
    '''
    Test the signup/login part of the app
    '''
    # Assign the flask app
    app = build_app()

    ### Test methods (mandatory, obviously) - should have client as a parameter

    def test_register(self, client: FlaskClient):
        self.signup(client, MockUser.username, MockUser.password)
        # Log in and delete the account
        self.login(client, MockUser.username, MockUser.password)
        self.delete(client)

    def test_login(self, client: FlaskClient):
        # Register an account first
        self.signup(client, MockUser.username, MockUser.password)
        # Log in
        self.login(client, MockUser.username, MockUser.password)

        # Make sure username shown on index page is correct
        rv: Response = client.get('/')
        soup = BeautifulSoup(rv.data, 'html.parser')
        self.assertEqual(soup.select_one('ul > li:nth-child(1) > span').text, MockUser.username)

        # Delete the account
        self.delete(client)

    def test_duplicate_register(self, client: FlaskClient):
        # Register an account
        self.signup(client, MockUser.username, MockUser.password)

        # Try registering for the same account again
        try:
            self.signup(client, MockUser.username, MockUser.password)
            raise AssertionError('Signup should have failed')
        except AssertionError as e:
            if 'Signup should have failed' in e.args:
                # Rethrow this exception since it should not be ignored
                raise e
            # Ignore the assertion error from signup method

        # Log in and delete the account
        self.login(client, MockUser.username, MockUser.password)
        self.delete(client)

    def test_invalid_login(self, client: FlaskClient):
        try:
            self.login(client, MockUser.username, MockUser.password)
            raise AssertionError('Login should have failed but it succeeded')
        except AssertionError as e:
            if 'Login should have failed' in e.args:
                # Re raise the exception if it was raised manually after login
                # i.e login somehow succeeded - even though it shouldn't have
                raise e
            # Ignore the assertion error from login method


class TestBlog(TestBase):
    '''
    Test the blog posts functionality of the app
    '''
    posts = MockPosts.posts
    # Assign the flask app
    app = build_app()

    ### setUp and tearDown methods per testcase (not mandatory) - should have client as a param

    def setUp(self, client: FlaskClient):
        # Create an account and log in with it
        self.signup(client, MockUser.username, MockUser.password)
        self.login(client, MockUser.username, MockUser.password)

    def tearDown(self, client: FlaskClient):
        # Delete the signed in account
        self.delete(client)

    ### Helper functions (not mandatory)

    def get_post_edit_link(self, rv: Response, title: str) -> str:
        # Find the element that has the correct title (of post)
        # The 2nd level parent of this element has an anchor tag as a child
        # The href of this anchor tag is the edit link
        soup = BeautifulSoup(rv.data, 'html.parser')
        post_h1: PageElement = [h1 for h1 in soup.select('article.post > header > div > h1') if h1.text == title][0]
        return post_h1.parent.parent.select_one('a')['href']

    def get_post_delete_link(self, rv: Response, title: str) -> str:
        # The delete link is just the same as the edit link, with the `edit` replaced with `delete`
        return self.get_post_edit_link(rv, title).replace('edit', 'delete')

    def verify_post_exists(self, rv: Response, title: str, body: str):
        # Make sure the given post exists in the given response html
        soup = BeautifulSoup(rv.data, 'html.parser')
        post_titles = [h1.text for h1 in soup.select('article.post > header > div > h1')]
        self.assertIn(title, post_titles)
        post_bodies = [p.text for p in soup.select('article.post > p')]
        self.assertIn(body, post_bodies)

    def create_post(self, client: FlaskClient, title: str, body: str):
        # Creates a post and verifies its presence on the index page
        rv: Response = client.post('/create', data={'title': title, 'body': body}, follow_redirects=True)
        # Make sure the post creation was succesful and the new post is present on the index page
        self.verify_post_exists(rv, title, body)

    def edit_post(self, client: FlaskClient, old_title: str, new_title: str, new_body: str):
        # Go to the index page to find the post
        rv: Response = client.get('/')

        # Get the edit link from the response html
        edit_link = self.get_post_edit_link(rv, old_title)
        rv: Response = client.post(edit_link, data={'title': new_title, 'body': new_body}, follow_redirects=True)

        # Make sure the post edit was succesful and the new post is present on the index page
        self.verify_post_exists(rv, new_title, new_body)

    def delete_post(self, client: FlaskClient, title: str, body: str):
        # Go to the index page to find the post
        rv: Response = client.get('/')

        # Get the delete link from the response html
        delete_link = self.get_post_edit_link(rv, title)
        rv: Response = client.post(delete_link, follow_redirects=True)

        # Make sure the post edit was succesful and the post has been deleted from the index page
        try:
            self.verify_post_exists(rv, title, body)
            raise AssertionError('Post should have been deleted but was found in page')
        except AssertionError as e:
            if 'Post should have been deleted' in e.args:
                # Re raise the exception if it was raised manually after verify_post_exists
                # i.e verify_post_exists somehow succeeded - even though it shouldn't have
                raise e
            # Ignore the assertion error from verify_post_exists method

    ### Test methods (mandatory, obviously) - should have client as a parameter

    def test_index_after_login(self, client: FlaskClient):
        # Make sure the setUp actually worked and the client is logged in
        rv: Response = client.get('/')
        soup = BeautifulSoup(rv.data, 'html.parser')
        self.assertEqual(soup.select_one('ul > li:nth-child(1) > span').text, MockUser.username)
        self.assertTrue(soup.select('a[href="/auth/logout"]'))
        self.assertTrue(soup.select('a[href="/auth/delete"]'))

    def test_post_creation(self, client: FlaskClient):
        # Create a post and check its presentation in the index page
        self.create_post(client, self.posts[0].title, self.posts[0].body)

    def test_post_edit(self, client: FlaskClient):
        # Create and edit a post
        self.create_post(client, self.posts[0].title, self.posts[0].body)
        self.edit_post(client, self.posts[0].title, self.posts[2].title, self.posts[2].body)

    def test_post_delete(self, client: FlaskClient):
        # Create and delete a post
        self.create_post(client, self.posts[1].title, self.posts[1].body)
        self.delete_post(client, self.posts[1].title, self.posts[1].body)

    def test_unauthorized_post_edit(self, client: FlaskClient):
        # Make sure posts aren't editable by non post owners
        self.create_post(client, self.posts[0].title, self.posts[0].body)

        # Logout and check if the edit button on the post exists
        self.logout(client)
        rv: Response = client.get('/')

        try:
            self.get_post_edit_link(rv, self.posts[0].title)
            raise AssertionError('Edit link should not have been found')
        except TypeError:
            # Ignore the type error from get_post_edit_link
            pass

        # Log back in as to not screw up the tearDown
        self.login(client, MockUser.username, MockUser.password)


if __name__ == '__main__':
    unittest.main()
