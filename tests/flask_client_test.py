import unittest
from typing import Type, Union

import flask_unittest
from flask.app import Flask
from flask.testing import FlaskClient
from flask.wrappers import Response
from bs4 import BeautifulSoup
from bs4.element import PageElement

from tests.app_factory import build_app


class MockUser:
    username = 'Marty_McFly'
    password = 'Ac1d1f1c4t10n@sh4rk'


class MockPost:
    title: Union[str, None] = None
    body: Union[str, None] = None
    def __init__(self, title: str, body: str):
        self.title = title
        self.body = body


class Posts:
    def __init__(self):
        self.posts = (
            MockPost('Finite time', 'Chances last a finite time'),
            MockPost('Walt Disney', 'Seven months of suicide'),
            MockPost('Turned away', 'Turn back the clock\nFall onto the ground')
        )


class TestSetup(flask_unittest.ClientTestCase):
    # Assign the flask app
    app = build_app()

    def setUp(self, client: FlaskClient):
        # Make sure client is passed in correctly and has correct type
        self.assertTrue(client is not None)
        self.assertTrue(isinstance(client, FlaskClient))

    def test_setup(self, client: FlaskClient):
        # Make sure the testcase is set up all correctly
        # i.e make sure the properties were injected
        self.assertTrue(client is not None)
        self.assertTrue(self.app is not None)

    def test_values(self, client: FlaskClient):
        # Make sure the properties are of correct type/value
        self.assertTrue(isinstance(self.app, Flask))
        self.assertTrue(isinstance(client, FlaskClient))
    
    def tearDown(self, client: FlaskClient):
        # Make sure client is passed in correctly and has correct type
        self.assertTrue(client is not None)
        self.assertTrue(isinstance(client, FlaskClient))


class TestIndex(flask_unittest.ClientTestCase):
    # Assign the flask app
    app = build_app()

    def test_presence_of_links(self, client: FlaskClient):
        # Make sure the register and login links are present in index page
        rv: Response = client.get('/')
        soup = BeautifulSoup(rv.data, 'html.parser')
        self.assertTrue(soup.select('a[href="/auth/register"]'))
        self.assertTrue(soup.select('a[href="/auth/login"]'))


class TestBase(flask_unittest.ClientTestCase):
    userdata = MockUser()
    # Make the test client use cookies - required for auth
    test_client_use_cookies = True

    def signup(self, client: FlaskClient, username: str, password: str):
        # Sign up with given credentials
        rv: Response = client.post('/auth/register', data={'username': username, 'password': password}, follow_redirects=True)
        soup = BeautifulSoup(rv.data, 'html.parser')
        # Make sure the log in page is showing
        self.assertIn('Log In', soup.find('title').text)

    def login(self, client: FlaskClient, username: str, password: str):
        # Log in with given credentials
        rv: Response = client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True)
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

class TestAuth(TestBase):
    '''
    Test the signup/login part of the app
    '''
    # Assign the flask app
    app = build_app()

    def test_register(self, client: FlaskClient):
        self.signup(client, self.userdata.username, self.userdata.password)
        # Log in and delete the account
        self.login(client, self.userdata.username, self.userdata.password)
        self.delete(client)

    def test_login(self, client: FlaskClient):
        # Register an account first
        self.signup(client, self.userdata.username, self.userdata.password)
        # Log in
        self.login(client, self.userdata.username, self.userdata.password)
        # Make sure username shown on index page is correct
        rv: Response = client.get('/')
        soup = BeautifulSoup(rv.data, 'html.parser')
        self.assertEqual(soup.select_one('ul > li:nth-child(1) > span').text, self.userdata.username)
        # Delete the account
        self.delete(client)

    def test_duplicate_register(self, client: FlaskClient):
        # Register an account
        self.signup(client, self.userdata.username, self.userdata.password)
        try:
            self.signup(client, self.userdata.username, self.userdata.password)
            raise AssertionError('Signup should have failed')
        except AssertionError as e:
            if 'Signup should have failed' in e.args:
                # Rethrow this exception since it should not be ignored
                raise e
            # Ignore the assertion error from signup method
        # Log back in and delete the account
        self.login(client, self.userdata.username, self.userdata.password)
        self.delete(client)

    def test_invalid_login(self, client: FlaskClient):
        try:
            self.login(client, self.userdata.username, self.userdata.password)
            raise AssertionError('Login should have failed')
        except AssertionError as e:
            if 'Login should have failed' in e.args:
                # Rethrow this exception since it should not be ignored
                raise e
            # Ignore the assertion error from login method

class TestBlog(TestBase):
    '''
    Test the blog posts functionality of the app
    '''
    posts = Posts().posts
    # Assign the flask app
    app = build_app()

    def setUp(self, client: FlaskClient):
        self.signup(client, self.userdata.username, self.userdata.password)
        self.login(client, self.userdata.username, self.userdata.password)

    def tearDown(self, client: FlaskClient):
        self.delete(client)

    def create_post(self, client: FlaskClient, title: str, body: str):
        # Creates a post and verifies its presence on the index page
        rv: Response = client.post('/create', data={'title': title, 'body': body}, follow_redirects=True)
        # Make sure the post creation was succesful and the new post is present on the index page
        soup = BeautifulSoup(rv.data, 'html.parser')
        post_titles = [h1.text for h1 in soup.select('article.post > header > div > h1')]
        self.assertIn(title, post_titles)
        post_bodies = [p.text for p in soup.select('article.post > p')]
        self.assertIn(body, post_bodies)

    def edit_post(self, client: FlaskClient, old_title: str, new_title: str, new_body: str):
        # Go to the index page and find the post to get the edit link
        rv: Response = client.get('/')
        soup = BeautifulSoup(rv.data, 'html.parser')
        post_h1: PageElement = [h1 for h1 in soup.select('article.post > header > div > h1') if h1.text == old_title][0]
        edit_link: str = post_h1.parent.parent.select_one('a')['href']
        rv: Response = client.post(edit_link, data={'title': new_title, 'body': new_body}, follow_redirects=True)
        # Make sure the post edit was succesful and the new post is present on the index page
        soup = BeautifulSoup(rv.data, 'html.parser')
        post_titles = [h1.text for h1 in soup.select('article.post > header > div > h1')]
        self.assertIn(new_title, post_titles)
        post_bodies = [p.text for p in soup.select('article.post > p')]
        self.assertIn(new_body, post_bodies)

    def delete_post(self, client: FlaskClient, title: str, body: str):
        # Go to the index page and find the post to get the delete link
        rv: Response = client.get('/')
        soup = BeautifulSoup(rv.data, 'html.parser')
        post_h1: PageElement = [h1 for h1 in soup.select('article.post > header > div > h1') if h1.text == title][0]
        delete_link: str = post_h1.parent.parent.select_one('a')['href'].replace('edit', 'delete')
        rv: Response = client.post(delete_link, follow_redirects=True)
        # Make sure the post edit was succesful and the post has been deleted from the index page
        soup = BeautifulSoup(rv.data, 'html.parser')
        post_titles = [h1.text for h1 in soup.select('article.post > header > div > h1')]
        self.assertNotIn(title, post_titles)
        post_bodies = [p.text for p in soup.select('article.post > p')]
        self.assertNotIn(body, post_bodies)

    def test_index_after_login(self, client: FlaskClient):
        # Make sure the setUp actually worked and the client is logged in
        rv: Response = client.get('/')
        soup = BeautifulSoup(rv.data, 'html.parser')
        self.assertEqual(soup.select_one('ul > li:nth-child(1) > span').text, self.userdata.username)
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
        soup = BeautifulSoup(rv.data, 'html.parser')
        post_h1: PageElement = [h1 for h1 in soup.select('article.post > header > div > h1') if h1.text == self.posts[0].title][0]
        try:
            post_h1.parent.parent.select_one('a')['href']
            raise AssertionError('Edit link should not have been found')
        except TypeError:
            pass
        # Log back in as to not screw up the tearDown
        self.login(client, self.userdata.username, self.userdata.password)

if __name__ == '__main__':
    unittest.main()
