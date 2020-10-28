from typing import Union

import flask_unittest
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from tests.app_factory import app


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


class TestSetup(flask_unittest.LiveTestCase):
    '''
    Make sure the testcase has been properly set up
    and all expected properties exist and are correct
    '''
    def test_setup(self):
        # Make sure the testcase is set up all correctly
        # i.e make sure the properties were injected
        self.assertTrue(self.server_url is not None)
        self.assertTrue(self.app is not None)

    def test_values(self):
        # Make sure the injected values are correct
        self.assertEqual(self.app, app)
        self.assertEqual(self.server_url, f'http://127.0.0.1:{app.config.get("PORT", 5000)}')


class TestIndex(flask_unittest.LiveTestCase):
    driver: Union[Chrome, None] = None
    std_wait: Union[WebDriverWait, None] = None

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
    
    def test_presence_of_links(self):
        # Make sure the register and login links are present in index page
        self.driver.get(self.server_url)
        self.std_wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Register')))
        self.std_wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Log In')))


class TestBase(flask_unittest.LiveTestCase):
    '''
    Base TestCase that has common methods/properties all the actual testcases will use
    '''
    driver: Union[Chrome, None] = None
    std_wait: Union[WebDriverWait, None] = None
    short_wait: Union[WebDriverWait, None] = None
    userdata = MockUser()

    @classmethod
    def setUpClass(cls):
        # Initiate the selenium webdriver
        options = ChromeOptions()
        options.add_argument('--headless')
        cls.driver = Chrome(options=options)
        cls.std_wait = WebDriverWait(cls.driver, 5)
        cls.short_wait = WebDriverWait(cls.driver, 1)
    
    @classmethod
    def tearDownClass(cls):
        # Quit the webdriver
        cls.driver.quit()

    def signup(self, username, password):
        self.driver.get(f'{self.server_url}/auth/register')
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(username)
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()
        # Make sure the signup was succesful and selenium was redirected to login page
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/section/header/h1[contains(text(), "Log In")]'))
        )

    def login(self, username, password):
        self.driver.get(f'{self.server_url}/auth/login')
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(username)
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()
        # Make sure the login was succesful and selenium was redirected to index page
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/section/header/h1[contains(text(), "Posts")]'))
        )

    def logout(self):
        # Logs out of the signed in account
        self.driver.get(f'{self.server_url}/auth/logout')
        # Make sure the logout was succesful and selenium was redirected to index page
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/section/header/h1[contains(text(), "Posts")]'))
        )
    
    def delete(self):
        # Deletes the signed in account
        self.driver.get(f'{self.server_url}/auth/delete')
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()
        # Make sure the delete was succesful and selenium was redirected to index page
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/section/header/h1[contains(text(), "Posts")]'))
        )


class TestAuth(TestBase):
    '''
    Test the signup/login part of the app
    '''
    def test_register(self):
        self.signup(self.userdata.username, self.userdata.password)
        # Log in and delete the account
        self.login(self.userdata.username, self.userdata.password)
        self.delete()

    def test_login(self):
        self.signup(self.userdata.username, self.userdata.password)
        # logout and log back in
        self.logout()
        self.login(self.userdata.username, self.userdata.password)
        # Go to index page and make sure username shown is correct
        self.driver.get(self.server_url)
        self.assertEqual(
            self.std_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'ul > li:nth-child(1) > span'))).text,
            self.userdata.username)
        # Delete the account
        self.delete()

    def test_duplicate_register(self):
        self.signup(self.userdata.username, self.userdata.password)
        # logout and sign up with the same credentials
        self.logout()
        try:
            self.signup(self.userdata.username, self.userdata.password)
            raise AssertionError('Signup should have failed')
        except Exception as e:
            pass
        # Log back in and delete the account
        self.login(self.userdata.username, self.userdata.password)
        self.delete()

    def test_invalid_login(self):
        try:
            self.login('definitely not real', 'supah secret')
            raise AssertionError('Login should have failed')
        except:
            pass


class TestBlog(TestBase):
    '''
    Test the blog posts functionality of the app
    '''
    posts = Posts().posts

    def setUp(self):
        self.signup(self.userdata.username, self.userdata.password)
        self.login(self.userdata.username, self.userdata.password)

    def tearDown(self):
        self.delete()

    def create_post(self, title, body):
        # Creates a post and verifies its presence on the index page
        self.driver.get(f'{self.server_url}/create')
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'title'))).send_keys(title)
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'body'))).send_keys(body)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()
        # Make sure the post creation was succesful and the new post is present on the index page
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, f'/html/body/section/article[@class="post"]/header/div/h1[contains(text(), "{title}")]'))
        )
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, f'/html/body/section/article[@class="post"]/p[contains(text(), "{body}")]'))
        )

    def edit_post(self, old_title, old_body, new_title, new_body):
        self.driver.get(self.server_url)
        # Go to the edit page of the given post
        self.std_wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'/html/body/section/article[@class="post"]/header[div/h1[contains(text(), "{old_title}")]]/a'))
        ).click()

        # Make sure the pre existing values in the fields are correct
        title_field = self.std_wait.until(EC.presence_of_element_located((By.ID, 'title')))
        body_field = self.std_wait.until(EC.presence_of_element_located((By.ID, 'body')))
        self.assertEqual(title_field.get_attribute('value'), old_title)
        self.assertEqual(body_field.get_attribute('value'), old_body)

        # Clear the fields and edit in new data
        title_field.clear()
        body_field.clear()
        title_field.send_keys(new_title)
        body_field.send_keys(new_body)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"][value="Save"]'))).click()

        # Make sure the post creation was succesful and the new post is present on the index page
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, f'/html/body/section/article[@class="post"]/header/div/h1[contains(text(), "{new_title}")]'))
        )
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, f'/html/body/section/article[@class="post"]/p[contains(text(), "{new_body}")]'))
        )

    def delete_post(self, title, body):
        self.driver.get(self.server_url)
        # Go to the edit page of the given post
        self.std_wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'/html/body/section/article[@class="post"]/header[div/h1[contains(text(), "{title}")]]/a'))
        ).click()

        # Make sure the pre existing values in the fields are correct
        title_field = self.std_wait.until(EC.presence_of_element_located((By.ID, 'title')))
        body_field = self.std_wait.until(EC.presence_of_element_located((By.ID, 'body')))
        self.assertEqual(title_field.get_attribute('value'), title)
        self.assertEqual(body_field.get_attribute('value'), body)

        # Delete the post
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"][value="Delete"]'))).click()
        self.std_wait.until(EC.alert_is_present()).accept()

        # Make sure deletion was successful and selenium was redirected to index page
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/section/header/h1[contains(text(), "Posts")]'))
        )
        # Also make sure the post does not exist anymore
        try:
            self.short_wait.until(EC.presence_of_element_located(
                (By.XPATH, f'/html/body/section/article[@class="post"]/header/div/h1[contains(text(), "{title}")]'))
            )
            raise AssertionError('Post should have been deleted but it was found')
        except TimeoutException:
            # Element does not exist - as expected
            pass

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
        self.driver.get(self.server_url)
        # Wait for index page to load
        self.std_wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/section/header/h1[contains(text(), "Posts")]'))
        )
        # Make sure the edit anchor tag does not exist
        try:
            self.short_wait.until(EC.element_to_be_clickable(
                (By.XPATH, f'/html/body/section/article[@class="post"]/header[div/h1[contains(text(), "{self.posts[0].title}")]]/a'))
            )
            raise AssertionError('Post should not be editable by logged out user')
        except TimeoutException:
            pass
        # Log back in as to not screw up the tearDown
        self.login(self.userdata.username, self.userdata.password)

if __name__ == '__main__':
    flask_unittest.main_live(app)
