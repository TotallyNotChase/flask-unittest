import unittest

from tests import livesuite, normalsuite


def run():
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(livesuite())
    runner.run(normalsuite())


if __name__ == '__main__':
    run()
