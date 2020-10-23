from typing import Union

import flask_unittest
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.app_factory import app

class MockUser:
    username = 'Marty_McFly'
    password = 'Ac1d1f1c4t10n@sh4rk'

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
        self.std_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/auth/register"]')))
        self.std_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/auth/login"]')))


class TestAuth(flask_unittest.LiveTestCase):
    driver: Union[Chrome, None] = None
    std_wait: Union[WebDriverWait, None] = None
    userdata = MockUser()

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

    def signup(self, username, password):
        self.driver.get(f'{self.server_url}/auth/register')
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(username)
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()
        # Make sure the signup was succesful and selenium was redirected to login page
        self.std_wait.until(EC.presence_of_element_located((By.XPATH, '//h1[contains(text(), "Log In")]')))

    def login(self, username, password):
        self.driver.get(f'{self.server_url}/auth/login')
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(username)
        self.std_wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()
        # Make sure the login was succesful and selenium was redirected to index page
        self.std_wait.until(EC.presence_of_element_located((By.XPATH, '//h1[contains(text(), "Posts")]')))

    def logout(self):
        # Logs out of the signed in account
        self.driver.get(f'{self.server_url}/auth/logout')
        # Make sure the logout was succesful and selenium was redirected to index page
        self.std_wait.until(EC.presence_of_element_located((By.XPATH, '//h1[contains(text(), "Posts")]')))
    
    def delete(self):
        # Deletes the signed in account
        self.driver.get(f'{self.server_url}/auth/delete')
        self.std_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))).click()
        # Make sure the delete was succesful and selenium was redirected to index page
        self.std_wait.until(EC.presence_of_element_located((By.XPATH, '//h1[contains(text(), "Posts")]')))

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
