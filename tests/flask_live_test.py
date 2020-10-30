from typing import Union

import flask_unittest
from flask.app import Flask
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from tests.app_factory import build_app
from tests.mockdata import MockUser, MockPosts


class TestBase(flask_unittest.LiveTestCase):
    '''
    Base ClientTestCase with helper functions used across other testcases

    Also sets up common properties

    Note this class should only be extended, it does not have any tests

    NOTE: You absolutely don't need to have a TestBase class to write tests. It's just
    convenient in this case since the other testcases share the same methods/properties.
    As long as your testcase class extends flask_unittest.LiveTestCase, and is used
    in conjuction with flask_unittest.LiveTestSuite - it's fine
    '''
    driver: Union[Chrome, None] = None
    std_wait: Union[WebDriverWait, None] = None

    ### setUpClass and tearDownClass for the entire class
    # Not quite mandatory, but this is the best place to set up and tear down selenium

    @classmethod
    def setUpClass(cls):
        # Initiate the selenium webdriver
        options = ChromeOptions()
        options.add_argument('--headless')
        cls.driver = Chrome(options=options)
        cls.std_wait = WebDriverWait(cls.driver, 5)

    @classmethod
    def tearDownClass(cls):
        # Quit the webdriver
        cls.driver.quit()

    ### Helper functions (not mandatory)

    def signup(self, username: str, password: str):
        # Sign up with given credentials
        self.driver.get(f'{self.server_url}/auth/register')
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(username)
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()

        # Make sure the signup was succesful and selenium was redirected to login page
        self.std_wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/section/header/h1[contains(text(), "Log In")]'))
        )

    def login(self, username: str, password: str):
        # Log in with given credentials
        self.driver.get(f'{self.server_url}/auth/login')
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(username)
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()

        # Make sure the login was succesful and selenium was redirected to index page
        self.std_wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/section/header/h1[contains(text(), "Posts")]'))
        )

    def logout(self):
        # Logs out of the signed in account
        self.driver.get(f'{self.server_url}/auth/logout')

        # Make sure the logout was succesful and selenium was redirected to index page
        self.std_wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/section/header/h1[contains(text(), "Posts")]'))
        )

    def delete(self):
        # Deletes the signed in account
        self.driver.get(f'{self.server_url}/auth/delete')
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()

        # Make sure the delete was succesful and selenium was redirected to index page
        self.std_wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/section/header/h1[contains(text(), "Posts")]'))
        )


class TestSetup(TestBase):
    '''
    Make sure the testcase has been properly set up
    and all expected properties exist and are correct
    '''

    ### Test methods (mandatory, obviously)

    def test_setup(self):
        # Make sure the testcase is set up all correctly
        # i.e make sure the properties were injected
        self.assertTrue(self.server_url is not None)
        self.assertTrue(self.app is not None)

    def test_values(self):
        # Make sure the injected types/values are correct
        self.assertTrue(isinstance(self.app, Flask))
        self.assertEqual(self.server_url, f'http://127.0.0.1:{self.app.config.get("PORT", 5000)}')


class TestIndex(TestBase):
    '''
    Test the index page
    '''
    driver: Union[Chrome, None] = None
    std_wait: Union[WebDriverWait, None] = None

    ### setUpClass and tearDownClass for the entire class
    # Not quite mandatory, but this is the best place to set up and tear down selenium

    @classmethod
    def setUpClass(cls):
        # Initiate the selenium webdriver
        options = ChromeOptions()
        options.add_argument('--headless')
        cls.driver = Chrome(options=options)
        cls.std_wait = WebDriverWait(cls.driver, 5)

    @classmethod
    def tearDownClass(cls):
        # Quit the webdriver
        cls.driver.quit()

    ### Test methods (mandatory, obviously)

    def test_presence_of_links(self):
        # Make sure the register and login links are present in index page
        self.driver.get(self.server_url)
        self.std_wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Register')))
        self.std_wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Log In')))


class TestAuth(TestBase):
    '''
    Test the signup/login part of the app
    '''

    ### Test methods (mandatory, obviously)

    def test_register(self):
        self.signup(MockUser.username, MockUser.password)
        # Log in and delete the account
        self.login(MockUser.username, MockUser.password)
        self.delete()

    def test_login(self):
        # Register an account first
        self.signup(MockUser.username, MockUser.password)
        # Log in
        self.login(MockUser.username, MockUser.password)

        # Go to index page and make sure username shown is correct
        self.driver.get(self.server_url)
        self.assertEqual(
            self.std_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul > li:nth-child(1) > span'))).text,
            MockUser.username
        )

        # Delete the account
        self.delete()

    def test_duplicate_register(self):
        # Register an account
        self.signup(MockUser.username, MockUser.password)

        # Try registering for the same account again
        try:
            self.signup(MockUser.username, MockUser.password)
            raise AssertionError('Signup should have failed')
        except TimeoutException:
            # Ignore the TimeoutException raised by `self.signup`
            pass

        # Log in and delete the account
        self.login(MockUser.username, MockUser.password)
        self.delete()

    def test_invalid_login(self):
        try:
            self.login('definitely not real', 'supah secret')
            raise AssertionError('Login should have failed')
        except TimeoutException:
            # Ignore the TimeoutException raised by `self.login`
            pass


class TestBlog(TestBase):
    '''
    Test the blog posts functionality of the app
    '''
    posts = MockPosts.posts

    ### setUp and tearDown methods per testcase (not mandatory)

    def setUp(self):
        self.signup(MockUser.username, MockUser.password)
        self.login(MockUser.username, MockUser.password)

    def tearDown(self):
        self.delete()

    ### Helper functions (not mandatory)

    def go_to_edit_page(self, title: str, body: str):
        # Go to the edit page of given post - located by title
        self.std_wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f'/html/body/section/article[@class="post"]/header[div/h1[contains(text(), "{title}")]]/a')
            )
        ).click()

        # Make sure the pre existing values in the fields are correct
        title_field = self.std_wait.until(EC.presence_of_element_located((By.ID, 'title')))
        body_field = self.std_wait.until(EC.presence_of_element_located((By.ID, 'body')))
        self.assertEqual(title_field.get_attribute('value'), title)
        self.assertEqual(body_field.get_attribute('value'), body)

    def verify_post_exists(self, title: str, body: str):
        # Make sure the given post exists in the index page
        self.driver.get(self.server_url)
        self.std_wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f'/html/body/section/article[@class="post"]/header/div/h1[contains(text(), "{title}")]')
            )
        )
        self.std_wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f'/html/body/section/article[@class="post"]/p[contains(text(), "{body}")]')
            )
        )

    def create_post(self, title: str, body: str):
        # Creates a post and verifies its presence on the index page
        self.driver.get(f'{self.server_url}/create')
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'title'))).send_keys(title)
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'body'))).send_keys(body)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()

        # Make sure the post creation was succesful and the new post is present on the index page
        self.verify_post_exists(title, body)

    def edit_post(self, old_title: str, old_body: str, new_title: str, new_body: str):
        self.driver.get(self.server_url)

        # Go to the edit form page of the post
        self.go_to_edit_page(old_title, old_body)
        # Clear the fields and edit in new data
        title_field = self.std_wait.until(EC.presence_of_element_located((By.ID, 'title')))
        body_field = self.std_wait.until(EC.presence_of_element_located((By.ID, 'body')))
        title_field.clear()
        body_field.clear()
        title_field.send_keys(new_title)
        body_field.send_keys(new_body)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"][value="Save"]'))).click()

        # Make sure the post creation was succesful and the new post is present on the index page
        self.verify_post_exists(new_title, new_body)

    def delete_post(self, title: str, body: str):
        self.driver.get(self.server_url)

        # Go to the edit form page of the post
        self.go_to_edit_page(title, body)
        # Delete the post
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"][value="Delete"]'))
                            ).click()
        self.std_wait.until(EC.alert_is_present()).accept()

        # Make sure deletion was successful and the post does not exist anymore
        try:
            self.verify_post_exists(title, body)
            raise AssertionError('Post should have been deleted but it was found')
        except TimeoutException:
            # Element does not exist - as expected
            pass

    ### Test methods (mandatory, obviously)

    def test_index_after_login(self):
        # Make sure the the correct links show in index page if logged in
        self.driver.get(self.server_url)
        self.std_wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Log Out')))
        self.std_wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Delete Me!')))
        self.std_wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'New')))

    def test_post_creation(self):
        # Create a post and check its presentation in the index page
        self.create_post(self.posts[0].title, self.posts[0].body)

    def test_post_edit(self):
        # Create and edit a post
        self.create_post(self.posts[0].title, self.posts[0].body)
        self.edit_post(self.posts[0].title, self.posts[0].body, self.posts[2].title, self.posts[2].body)

    def test_post_delete(self):
        # Create and delete a post
        self.create_post(self.posts[1].title, self.posts[1].body)
        self.delete_post(self.posts[1].title, self.posts[1].body)

    def test_unauthorized_post_edit(self):
        # Make sure posts aren't editable by non post owners
        self.create_post(self.posts[0].title, self.posts[0].body)

        # Logout and check if the edit button on the post exists
        self.logout()

        # Make sure the edit anchor tag does not exist
        try:
            self.go_to_edit_page(self.posts[0].title, self.posts[0].body)
            raise AssertionError('Post should not be editable by logged out user')
        except TimeoutException:
            # Element does not exist - as expected
            pass

        # Log back in as to not screw up the tearDown
        self.login(MockUser.username, MockUser.password)


if __name__ == '__main__':
    # WARNING: `main_live` is currently **EXPERIMENTAL**
    # Please consider using the suite manually as seen in `tests/__init__.py`
    flask_unittest.main_live(build_app())
