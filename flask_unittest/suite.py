import unittest
import threading
import socket
from typing import Union, Iterator, Iterable

from flask import Flask

from .case import TestCase

_TestType = Union[TestCase, unittest.TestSuite]

# Imitate socket.create_connection's placeholder default timeout
_GLOBAL_DEFAULT_TIMEOUT = object()

# Store localhost as constant
_LOCALHOST = '127.0.0.1'

class TestSuite(unittest.TestSuite):
    # Handle for the flask server
    _thread: Union[threading.Thread, None] = None

    def __init__(self, flask_app: Flask, timeout: Union[float, None]=_GLOBAL_DEFAULT_TIMEOUT, tests: Iterable[_TestType]=()):
        if flask_app.testing != True:
            # Passed app must be set to testing
            raise AttributeError(f'Expected flask_app.testing to have a value of True, got {flask_app.testing} instead')
        self.app = flask_app
        self.timeout = timeout if timeout is not _GLOBAL_DEFAULT_TIMEOUT else None
        self._port: int = flask_app.config.get('PORT', 5000)
        super().__init__(tests)

    def run(self, result, debug=False):
        self._setup_server()
        self._setup_testcases()
        return super().run(result, debug)

    ### Private functions specific to flask-unittest testcases

    def _setup_testcases(self):
        # Set up required properties in all testcases in current testsuite
        for test in self:
            if self._isnotsuite(test):
                test.server_url = f'http://127.0.0.1:{self._port}'
            else:
                # Current element is an entire suite - iterate through it and add properties to each test
                for inner_test in test:
                    inner_test.server_url = f'http://127.0.0.1:{self._port}'

    def _setup_server(self):
        # Spawn the flask server as a separate process
        self._thread = threading.Thread(target=self.app.run, kwargs={ 'port': self._port, 'use_reloader': False })
        self._thread.setDaemon(True)
        self._thread.start()
        # Wait for the server to start responding, until a specific timeout
        sckt = socket.create_connection((_LOCALHOST, self._port), timeout=self.timeout or None)
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

