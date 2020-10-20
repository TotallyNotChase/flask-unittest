import unittest
from typing import Union

class TestCase(unittest.TestCase):
    _server_url: Union[str, None] = None

    @property
    def server_url(self):
        if self._server_url:
            return self._server_url
        # Property has not been set yet
        raise AttributeError
        
    @server_url.setter
    def server_url(self, url: str):
        self._server_url = url
