import unittest
import functools
from typing import Dict, Union, Optional

from flask import Flask
from flask.testing import FlaskClient
from flask.wrappers import Response


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


class UtilityTestCase(unittest.TestCase):
    '''
    Utility methods used by actual TestCases
    '''
    def assertStatus(self, rv: Response, expected_status: int):
        self.assertEqual(rv.status_code, expected_status)


class ClientTestCase(UtilityTestCase):
    '''
    Test your flask web app using a FlaskClient object

    A FlaskClient object is created using the given app object for **each**
    test set (i.e setUp, test method, tearDown) - this same object is then passed
    to the setUp, test method and tearDown
    The user can use this FlaskClient object to test api calls

    A built and instantiated Flask app object should
    be assigned to the `app` property

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

    def run(self, result: Optional[unittest.TestResult]) -> Optional[unittest.TestResult]:
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
                return super().run(result)
            finally:
                # Restore the original methods
                setattr(self, self._testMethodName, orig_test)
                self.setUp = orig_setup
                self.tearDown = orig_teardown

    def debug(self):
        # Almost identical to the run method above
        orig_test = getattr(self, self._testMethodName)
        orig_setup = self.setUp
        orig_teardown = self.tearDown
        # Instance the client
        with self.app.test_client(self.test_client_use_cookies, **self.test_client_kwargs) as client:
            try:
                '''
                Override the method to create a partially built method - pass in the client

                super().debug can now call this test method without passing anything and it'll all work out
                '''
                setattr(self, self._testMethodName, functools.partial(orig_test, client))
                # Also override the set up and tear down methods similarly
                self.setUp = functools.partial(orig_setup, client)
                self.tearDown = functools.partial(orig_teardown, client)
                # Call the actual test
                super().debug()
            finally:
                # Restore the original methods
                setattr(self, self._testMethodName, orig_test)
                self.setUp = orig_setup
                self.tearDown = orig_teardown


class AppTestCase(UtilityTestCase):
    '''
    Test your flask web app using a Flask object

    A Flask object is created by calling the create_app function for **each**
    test set (i.e setUp, test method, tearDown) - this same object is then passed
    to the setUp, test method and tearDown
    The user can use this Flask object to test the app

    The `create_app` function should create/configure/set up and return
    a Flask app object

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

    def run(self, result: Optional[unittest.TestResult]) -> Optional[unittest.TestResult]:
        '''
        The test method currently being tested should be in _testMethodName
        The method will be overridden a bit, so the original should be stored safely

        The set up and tear down methods will also be overriden and should also be stored
        '''
        orig_test = getattr(self, self._testMethodName)
        orig_setup = self.setUp
        orig_teardown = self.tearDown
        # Instance the app
        app = self.create_app()
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
            return super().run(result)
        finally:
            # Restore the original methods
            setattr(self, self._testMethodName, orig_test)
            self.setUp = orig_setup
            self.tearDown = orig_teardown

    def debug(self):
        # Almost identical to the run method above
        orig_test = getattr(self, self._testMethodName)
        orig_setup = self.setUp
        orig_teardown = self.tearDown
        # Instance the app
        app = self.create_app()
        try:
            '''
            Override the method to create a partially built method - pass in the app

            super().debug can now call this test method without passing anything and it'll all work out
            '''
            setattr(self, self._testMethodName, functools.partial(orig_test, app))
            # Also override the set up and tear down methods similarly
            self.setUp = functools.partial(orig_setup, app)
            self.tearDown = functools.partial(orig_teardown, app)
            # Call the actual test
            super().debug()
        finally:
            # Restore the original methods
            setattr(self, self._testMethodName, orig_test)
            self.setUp = orig_setup
            self.tearDown = orig_teardown


class AppClientTestCase(UtilityTestCase):
    '''
    Test your flask web app using a Flask object **and** a FlaskClient object

    A Flask and a FlaskClient object are created by calling the create_app function, and
    the `test_client` method on the Flask object for **each**
    test set (i.e setUp, test method, tearDown) - these same objects are then passed
    to the setUp, test method and tearDown
    The user can use these Flask and FlaskClient objects to test the app

    The `create_app` function should create/configure/set up and return
    a Flask app object

    Can be used with unittest.TestSuite
    '''
    # Whether or not to use cookies in test client
    test_client_use_cookies: bool = False
    # kwargs to pass to test_client function
    test_client_kwargs: Dict = {}

    def create_app(self) -> Flask:
        '''
        Should return a built/configured Flask app object

        To be implemented by the user
        '''
        raise NotImplementedError

    def setUp(self, app: Flask, client: FlaskClient) -> None:
        '''
        Set up to do before running each test
        '''
        pass

    def tearDown(self, app: Flask,  client: FlaskClient) -> None:
        '''
        Cleanup to do after running each test
        '''
        pass

    def run(self, result: Optional[unittest.TestResult]) -> Optional[unittest.TestResult]:
        '''
        The test method currently being tested should be in _testMethodName
        The method will be overridden a bit, so the original should be stored safely

        The set up and tear down methods will also be overriden and should also be stored
        '''
        orig_test = getattr(self, self._testMethodName)
        orig_setup = self.setUp
        orig_teardown = self.tearDown
        # Instance the app
        app = self.create_app()
        # Instance the client
        with app.test_client(self.test_client_use_cookies, **self.test_client_kwargs) as client:
            try:
                '''
                Override the method to create a partially built method - pass in the client

                super().run can now call this test method without passing anything and it'll all work out
                '''
                setattr(self, self._testMethodName, functools.partial(orig_test, app, client))
                # Also override the set up and tear down methods similarly
                self.setUp = functools.partial(orig_setup, app, client)
                self.tearDown = functools.partial(orig_teardown, app, client)
                # Call the actual test
                return super().run(result)
            finally:
                # Restore the original methods
                setattr(self, self._testMethodName, orig_test)
                self.setUp = orig_setup
                self.tearDown = orig_teardown

    def debug(self):
        # Almost identical to the run method above
        orig_test = getattr(self, self._testMethodName)
        orig_setup = self.setUp
        orig_teardown = self.tearDown
        # Instance the app
        app = self.create_app()
        # Instance the client
        with app.test_client(self.test_client_use_cookies, **self.test_client_kwargs) as client:
            try:
                '''
                Override the method to create a partially built method - pass in the client

                super().debug can now call this test method without passing anything and it'll all work out
                '''
                setattr(self, self._testMethodName, functools.partial(orig_test, app, client))
                # Also override the set up and tear down methods similarly
                self.setUp = functools.partial(orig_setup, app, client)
                self.tearDown = functools.partial(orig_teardown, app, client)
                # Call the actual test
                super().debug()
            finally:
                # Restore the original methods
                setattr(self, self._testMethodName, orig_test)
                self.setUp = orig_setup
                self.tearDown = orig_teardown
