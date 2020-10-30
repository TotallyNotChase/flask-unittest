import unittest

from tests import suite


def run():
    unittest.TextTestRunner(verbosity=2).run(suite())


if __name__ == '__main__':
    run()
