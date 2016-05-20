import unittest
import inspect
import codegen
from MuUtilities import *
import sys

class MuTester(object):

    @classmethod
    def run(cls, suite_module, module_to_test):
        """
        Runs all test cases in a specified test suite on an sut.
        Returns the raw test result.
        """
        delattr(suite_module, 'calculator')



        suite = unittest.TestLoader().loadTestsFromModule(suite_module)
        return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    suite_module_name = "sample.unittest_calculator"
    suite_module = ModuleLoader.load_single_module(suite_module_name)

    # run test
    test_result = MuTester.run(suite_module, None)

    print "Done!"
