import unittest
import threading
import socket
from typing import Union, Iterator, Iterable

from flask import Flask

from .case import LiveTestCase

_TestType = Union[LiveTestCase, unittest.TestSuite]

# A constant placeholder to signify default timeout parameter
_GLOBAL_DEFAULT_TIMEOUT = object()

# Store localhost as constant
_LOCALHOST = '127.0.0.1'


class LiveTestSuite(unittest.TestSuite):
    # Handle for the flask server
    _thread: Union[threading.Thread, None] = None

    def __init__(
        self, flask_app: Flask, timeout: Union[float, None] = _GLOBAL_DEFAULT_TIMEOUT, tests: Iterable[_TestType] = ()
    ):
        self._app = flask_app
        self._timeout = timeout if timeout is not _GLOBAL_DEFAULT_TIMEOUT else None
        self._host: str = flask_app.config.get('HOST', '127.0.0.1')
        self._port: int = flask_app.config.get('PORT', 5000)
        super().__init__(tests)

    def run(self, result, debug=False):
        self._setup_server()
        self._setup_testcases()
        return super().run(result, debug)

    ### Private helper methods

    def _setup_testcases(self):
        # Set up required properties in all testcases in current testsuite
        def _inject_properties(testcase: LiveTestCase):
            # Inject the required properties into the given test case
            testcase.server_url = f'http://127.0.0.1:{self._port}'
            testcase.app = self._app

        for test in self:
            if self._isnotsuite(test):
                _inject_properties(test)
            else:
                # Current element is an entire suite - iterate through it and add properties to each test
                for inner_test in test:
                    _inject_properties(inner_test)

    def _setup_server(self):
        # Spawn the flask server as a separate process
        self._thread = threading.Thread(target=self._app.run, kwargs={'host': self._host, 'port': self._port, 'use_reloader': False})
        self._thread.setDaemon(True)
        self._thread.start()
        # Wait for the server to start responding, until a specific timeout
        sckt = socket.create_connection((_LOCALHOST, self._port), timeout=self._timeout or None)
        sckt.close()

    def _isnotsuite(self, test):
        '''
        A crude way to tell apart testcases and suites with duck-typing

        Taken from unittest.TestSuite internals
        '''
        try:
            iter(test)
        except TypeError:
            return True
        return False

    ### Override the type hints of some derived functions

    def addTest(self, test: _TestType):
        super().addTest(test)

    def addTests(self, tests: Iterable[_TestType]):
        super().addTests(tests)

    def __iter__(self) -> Iterator[_TestType]:
        return super().__iter__()
