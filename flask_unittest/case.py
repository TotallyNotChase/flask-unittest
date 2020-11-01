import unittest
import functools
from inspect import isgeneratorfunction
from typing import Callable, Dict, Iterator, Union, Optional

from flask import Flask
from flask.testing import FlaskClient
from flask.wrappers import Response


class LiveTestCase(unittest.TestCase):
    '''
    Interacts with a live flask webserver running on a daemon thread

    The server is started when the TestSuite (not TestCase) runs
    The lifetime of the server is the full duration of the TestSuite

    If you're testing flask using a headless browser (e.g selenium) - this is the testcase
    you need

    Should be used with LiveTestSuite
    '''
    app: Union[Flask, None] = None
    server_url: Union[str, None] = None


class _TestCaseImpl(unittest.TestCase):
    '''
    Common methods all the following TestCases will use

    This will set up methods to wrap up the `super().run` and `super().debug` call
    Similar set up is used by all the following testcases - with only slight variation
    The variation room is left open - to be implemented in `_handle_resource_instantiation_and_internal_call`
    by the actual testcases themselves

    The common part of the setup is-
    * Store the original setUp, testMethod (i.e the actual test defined by user),
      and tearDown methods in temp variables
    * Wrap the `super().run` and `super().debug` in a `try/finally` block
    * Restore the original setUp, testMethod and tearDown methods in the `finally` block
    '''

    ### Utility functions exposed to the user

    def assertStatus(self, rv: Response, expected_status: int):
        # Assert the status code of given response
        self.assertEqual(rv.status_code, expected_status)

    def assertResponseEqual(self, rv: Response, expected_response):
        # Assert the expected_response is equal to the given response's .data
        self.assertEqual(rv.data, expected_response)

    def assertJsonEqual(self, rv: Response, expected_json: Dict):
        # Assert the expected_json is equal to the given response's .json
        self.assertEqual(rv.json, expected_json)

    def assertInResponse(self, member, rv: Response):
        # Assert the given member exists in response.data
        self.assertIn(member, rv.data)

    def assertLocationHeader(self, rv: Response, expected_location: str):
        # Assert the expected_location matches the location key present in the given response's header
        self.assertEqual(rv.headers['Location'], expected_location)

    ### Override run and debug to provide the extra functionality

    def run(self, result: Optional[unittest.TestResult]) -> Optional[unittest.TestResult]:
        '''
        Wrap the actual `super().run` call with all the custom setup

        Prepare `super().run` with `result` and pass it to the setup
        This way, the setup can just call `internal_method()` without having to pass `result`
        '''
        return self._wrap_internal_method_with_custom_setup(functools.partial(super().run, result))

    def debug(self):
        '''
        Wrap the actual super().debug call with all the custom setup
        '''
        return self._wrap_internal_method_with_custom_setup(super().debug)

    ### Private methods that implement the extra functionality

    def _wrap_internal_method_with_custom_setup(self, internal_method: Callable):
        '''
        The test method currently being tested should be in _testMethodName
        The method will be overridden a bit, so the original should be stored safely

        The set up and tear down methods will also be overriden and should also be stored
        '''
        orig_test = getattr(self, self._testMethodName)
        orig_setup = self.setUp
        orig_teardown = self.tearDown
        '''
        This will manage the actual instantiation of resources (creating app/client or both)
        + call `super().run`/`super().debug`
        + clean up after itself
        '''
        return self._handle_resource_instantiation_and_internal_call(
            internal_method, orig_test, orig_setup, orig_teardown
        )

    def _handle_resource_instantiation_and_internal_call(
        self, internal_method: Callable, orig_test: Callable, orig_setup: Callable, orig_teardown: Callable
    ):
        '''
        Instantiate the resources required by the specific testcase (i.e either app/client or both)
        Then call `_handle_try_finally_around_internal_call`, passing in the necessary parameters depending
        on the test case

        This is to be implemented by the actual testcase class (down below)
        Since each testcase instantiates different resources differently
        '''
        raise NotImplementedError

    def _handle_try_finally_around_internal_call(
        self,
        internal_method: Callable,
        orig_test: Callable,
        orig_setup: Callable,
        orig_teardown: Callable,
        *test_args,
        create_app_result: Union[Flask, Iterator[Flask], None] = None
    ):
        '''
        Override the test method and setUp, tearDown by preparing them with *test_args
        content of *test_args varies by testcase and should be passed by `_handle_resource_instantiation_and_internal_call`
        
        Then call the internal method (prepared `super().run`/`super().debug`)

        Then cleanup
        '''
        try:
            '''
            Override the method to create a partially built method - pass in the app/client or both (i.e *test_args)

            `super().run`/`super().debug` can now call this test method without passing anything and it'll all work out

            NOTE: if `internal_method` references `super().run` - it is already prepared with the required `TestResult` object
            so it can be called directly, same as `super().debug` - which does not require any parameters and hence can be
            called directly too
            The preparation is done in `_TestCaseImpl::run` (up above)
            '''
            setattr(self, self._testMethodName, functools.partial(orig_test, *test_args))
            # Also override the set up and tear down methods similarly
            self.setUp = functools.partial(orig_setup, *test_args)
            self.tearDown = functools.partial(orig_teardown, *test_args)
            # Call the actual test
            return internal_method()
        finally:
            if hasattr(self, '_teardown_create_app_result'):
                # If the object has _teardown_create_app_result method - it's a AppTestCase/AppClientTestCase
                # In which case, handle tearing down the result gotten from `create_app` (should be passed as an arg)
                getattr(self, '_teardown_create_app_result')(create_app_result)

            # Restore the original methods
            setattr(self, self._testMethodName, orig_test)
            self.setUp = orig_setup
            self.tearDown = orig_teardown


class ClientTestCase(_TestCaseImpl):
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
    test_client_use_cookies: bool = True
    # kwargs to pass to test_client function
    test_client_kwargs: Dict = {}

    def __init__(self, methodName='runTest'):
        # Verify self.app was provided
        if not self.app:
            raise NotImplementedError('property `app` must be assigned in ClientTestCase')
        # Call the original __init__
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

    def _handle_resource_instantiation_and_internal_call(
        self, internal_method: Callable, orig_test: Callable, orig_setup: Callable, orig_teardown: Callable
    ):
        '''
        ClientTestCase only needs to instantiate the client, in a with block
        Do just that, and pass the client to `_handle_try_finally_around_internal_call`, which will then
        pass it to the actual test method, setUp and tearDown
        '''
        with self.app.test_client(self.test_client_use_cookies, **self.test_client_kwargs) as client:
            return self._handle_try_finally_around_internal_call(
                internal_method, orig_test, orig_setup, orig_teardown, client
            )


class AppTestCase(_TestCaseImpl):
    '''
    Test your flask web app using a Flask object

    A Flask object is created by calling the create_app function for **each**
    test set (i.e setUp, test method, tearDown) - this same object is then passed
    to the setUp, test method and tearDown
    The user can use this Flask object to test the app

    The `create_app` function should create/configure/set up and return/yield
    a Flask app object

    Can be used with unittest.TestSuite
    '''
    def create_app(self) -> Union[Flask, Iterator[Flask]]:
        '''
        Should return/yield a built/configured Flask app object

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

    ### Private helper methods

    def _instantiate_app(self):
        if isgeneratorfunction(self.create_app):
            # create_app yields an iterator/generator
            res = self.create_app()
            return res, next(res)
        else:
            # create_app returns a regular object - hopefully a Flask object
            res = self.create_app()
            if not isinstance(res, Flask):
                raise TypeError(f'Expected create_app to return a Flask object - got {type(res)}')
            return res, res

    def _handle_resource_instantiation_and_internal_call(
        self, internal_method: Callable, orig_test: Callable, orig_setup: Callable, orig_teardown: Callable
    ):
        '''
        AppTestCase needs to instantiate the app
        It also has to handle generator/iterator cases, so use `_instantiate_app()`
        and pass the `res` to `_handle_try_finally_around_internal_call` as `create_app_result`
        which will then handle tearing it down if it was a generator/iterator
        
        Otherwise, the `app` needs to be passed to `_handle_try_finally_around_internal_call`, which will then
        pass it to the actual test method, setUp and tearDown
        '''
        res, app = self._instantiate_app()
        return self._handle_try_finally_around_internal_call(
            internal_method, orig_test, orig_setup, orig_teardown, app, create_app_result=res
        )

    def _teardown_create_app_result(self, res: Union[Flask, Iterator[Flask]]):
        # Tear down the result obtained by calling create_app
        # This is only here to handle when create_app returns a generator/iterator
        if isinstance(res, Flask):
            # create_app did not return a generator/iterator - nothing to clean up
            return
        else:
            # Teardown the generator/iterator
            try:
                next(res)
            except StopIteration:
                pass
            else:
                raise TypeError('Expected create_app to yield 1 value - got multiple')


class AppClientTestCase(AppTestCase):
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
    test_client_use_cookies: bool = True
    # kwargs to pass to test_client function
    test_client_kwargs: Dict = {}

    def setUp(self, app: Flask, client: FlaskClient) -> None:
        '''
        Set up to do before running each test
        '''
        pass

    def tearDown(self, app: Flask, client: FlaskClient) -> None:
        '''
        Cleanup to do after running each test
        '''
        pass

    def _handle_resource_instantiation_and_internal_call(
        self, internal_method: Callable, orig_test: Callable, orig_setup: Callable, orig_teardown: Callable
    ):
        '''
        AppClientTestCase needs to instantiate the app *and* the client
        It also has to handle generator/iterator cases, just like AppTestCase
        
        The `app` and `client` needs to be passed to `_handle_try_finally_around_internal_call`, which will then
        pass it to the actual test method, setUp and tearDown
        '''
        res, app = self._instantiate_app()
        with app.test_client(use_cookies=self.test_client_use_cookies, **self.test_client_kwargs) as client:
            return self._handle_try_finally_around_internal_call(
                internal_method, orig_test, orig_setup, orig_teardown, app, client, create_app_result=res
            )
