import unittest

class TestSuite(unittest.TestSuite):
    def run(self, result, debug=False):
        try:
            super().run(result, debug)
        finally:
            'no'
