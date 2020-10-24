import unittest
from typing import Union

from flask import Flask

from .loader import LiveTestLoader, defaultLiveTestLoader

# A constant placeholder to signify default timeout parameter
_GLOBAL_DEFAULT_TIMEOUT = object()

class LiveTestProgram(unittest.TestProgram):
    def __init__(self, flask_app: Flask, timeout: Union[float, None]=_GLOBAL_DEFAULT_TIMEOUT, module='__main__', defaultTest=None, argv=None,
                    testRunner=None, testLoader: Union[LiveTestLoader, None]=defaultLiveTestLoader,
                    exit=True, verbosity=1, failfast=None, catchbreak=None,
                    buffer=None, warnings=None, *, tb_locals=False):
        if testLoader is defaultLiveTestLoader:
            # Construct the default live test loader if no custom loader was provided
            testLoader = LiveTestLoader(flask_app, timeout if timeout is not _GLOBAL_DEFAULT_TIMEOUT else None)
        super().__init__(module, defaultTest, argv, testRunner, testLoader, exit, verbosity, failfast, catchbreak, buffer, warnings, tb_locals=tb_locals)

main_live = LiveTestProgram
