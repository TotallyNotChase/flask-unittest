import unittest
from typing import Union

from .suite import LiveTestSuite
from .utils import _partialclass

# A constant placeholder to signify default timeout parameter
_GLOBAL_DEFAULT_TIMEOUT = object()


class LiveTestLoader(unittest.TestLoader):
    suiteClass = LiveTestSuite

    def __init__(self, flask_app, timeout: Union[float, None] = _GLOBAL_DEFAULT_TIMEOUT):
        '''
        Partially construct the TestSuite class
        unittest.TestLoader works with unittest.TestSuite,
        which does not take an `flask_app` (also `timeout`) as a parameter during construction

        To avoid overriding every single method in LiveTestLoader just to pass in that
        extra `flask_app` (also `timeout`) parameter to `suiteClass` - turn suiteClass into a partially constructed LiveTestSuite
        This will make the construction process of LiveTestSuite (in later stages), exactly
        the same as unittest.TestSuite

        Basically, doing stuff like `self.suiteClass(map(testCaseClass, testCaseNames))`
        (something that is done in unittest.TestLoader) will work perfectly fine because the `flask_app` (also `timeout`)
        parameter has already been passed to `suiteClass` - but it hasn't been instantiated - it's still a class!
        '''

        self.suiteClass = _partialclass(
            LiveTestSuite, flask_app, timeout if timeout is not _GLOBAL_DEFAULT_TIMEOUT else None
        )
        super().__init__()


# A constant placeholder to signify default live test loader parameter
defaultLiveTestLoader = object()
