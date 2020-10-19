import unittest

from .case import TestCase
from .suite import TestSuite

def main(module='__main__'):
    #runner = unittest.TextTestRunner()
    #suite = unittest.TestSuite()
    print(dir(module))
    #runner.run(suite())
