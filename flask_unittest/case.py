import unittest

class TestCase(unittest.TestCase):
    @staticmethod
    def create_app():
        raise NotImplementedError
