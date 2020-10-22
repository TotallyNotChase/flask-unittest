import unittest
from typing import Union, ContextManager

from flask import Flask
from flask.ctx import RequestContext

class LiveTestCase(unittest.TestCase):
    app: Union[Flask, None] = None
    server_url: Union[str, None] = None

class ClientTestCase(unittest.TestCase):
    app: Union[Flask, None] = None
    req_ctx: Union[ContextManager[RequestContext], None] = None
    server_url: Union[str, None] = None
