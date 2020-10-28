import unittest
import functools
from typing import Dict, Union, Optional

from flask import Flask
from flask.testing import FlaskClient

class LiveTestCase(unittest.TestCase):
    '''
    Interacts with a live flask webserver running on a daemon thread

    The server is started when the TestSuite (not TestCase) runs
    The lifetime of the server is the full duration of the TestSuite (not TestCase)

    If you're testing flask using a headless browser (e.g selenium) - this is the testcase
    you need

    Should be used with LiveTestSuite
    '''
    app: Union[Flask, None] = None
    server_url: Union[str, None] = None

class ClientTestCase(unittest.TestCase):
    '''
    Test your flask web app using a FlaskClient object

    A built and instantiated Flask app object should
    be assigned to the `app` property
    This `app` property is used to yield a test client
    for each test, which is then passed to said test and
    its corresponding setUp and tearDown methods

    Can be used with unittest.TestSuite
    '''
    app: Union[Flask, None] = None
    # Whether or not to use cookies in test client
    test_client_use_cookies: bool = False
    # kwargs to pass to test_client function
    test_client_kwargs: Dict = {}

    def __init__(self, methodName='runTest'):
        # Verify self.app was provided
        if not self.app:
            raise NotImplementedError('property `app` must be assigned in ClientTestCase')
        # Verify self.app.testing is set to `True`
        if self.app.testing != True:
            # Created app must be set to testing
            raise AttributeError(f'Expected app.testing (where app is the result of `self.create_app()`) to have a value of True, got {self.app.testing} instead')
        super().__init__(methodName)

    def setUp(self, client: FlaskClient) -> None:
        '''
        Set up to do before running each test
        '''
        pass

    def tearDown(self, client: FlaskClient) -> None:
        '''
        Cleanup to do after running each test
        '''
        pass

    def run(self, result: Optional[unittest.result.TestResult]) -> Optional[unittest.result.TestResult]:
        '''
        The test method currently being tested should be in _testMethodName
        The method will be overridden a bit, so the original should be stored safely

        The set up and tear down methods will also be overriden and should also be stored
        '''
        orig_test = getattr(self, self._testMethodName)
        orig_setup = self.setUp
        orig_teardown = self.tearDown
        # Instance the client
        with self.app.test_client(self.test_client_use_cookies, **self.test_client_kwargs) as client:
            try:
                '''
                Override the method to create a partially built method - pass in the client

                super().run can now call this test method without passing anything and it'll all work out
                '''
                setattr(self, self._testMethodName, functools.partial(orig_test, client))
                # Also override the set up and tear down methods similarly
                self.setUp = functools.partial(orig_setup, client)
                self.tearDown = functools.partial(orig_teardown, client)
                # Call the actual test
                super().run(result)
            finally:
                # Restore the original methods
                setattr(self, self._testMethodName, orig_test)
                self.setUp = orig_setup
                self.tearDown = orig_teardown

class AppTestCase(unittest.TestCase):
    '''
    Test your flask web app using a Flask object

    The `create_app` function should create/configure/set up and return
    a Flask app object
    This function will be called for each test - the built app will be
    passed to the test, as well as its corresponding setUp and tearDown methods

    Can be used with unittest.TestSuite
    '''

    def create_app(self) -> Flask:
        '''
        Should return a built/configured Flask app object

        To be implemented by the user
        '''
        raise NotImplementedError

    def setUp(self, app: Flask) -> None:
        '''
        Set up to do before
        '''
        pass

    def tearDown(self, app: Flask) -> None:
        pass

    def run(self, result: Optional[unittest.result.TestResult]) -> Optional[unittest.result.TestResult]:
        '''
        The test method currently being tested should be in _testMethodName
        The method will be overridden a bit, so the original should be stored safely

        The set up and tear down methods will also be overriden and should also be stored
        '''
        orig_test = getattr(self, self._testMethodName)
        orig_setup = self.setUp
        orig_teardown = self.tearDown
        # Instance the app
        with self.create_app() as app:
            try:
                '''
                Override the method to create a partially built method - pass in the app

                super().run can now call this test method without passing anything and it'll all work out
                '''
                setattr(self, self._testMethodName, functools.partial(orig_test, app))
                # Also override the set up and tear down methods similarly
                self.setUp = functools.partial(orig_setup, app)
                self.tearDown = functools.partial(orig_teardown, app)
                # Call the actual test
                super().run(result)
            finally:
                # Restore the original methods
                setattr(self, self._testMethodName, orig_test)
                self.setUp = orig_setup
                self.tearDown = orig_teardown

