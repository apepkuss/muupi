import unittest
import inspect
import codegen
from MuUtilities import *
import sys
from multiprocessing import Process
from threading import Thread
import os
import ctypes


class MuTester(object):

    def __init__(self, test_suite_module):
        self.suite_module = test_suite_module
        # generate an instance of unittest.TestSuite
        self.suite = unittest.TestLoader().loadTestsFromModule(self.suite_module)

    def run(self):
        """
        Run all test cases in a specified test suite on target module under test.
        :return: the raw test result
        """
        return unittest.TextTestRunner(verbosity=2).run(self.suite)

    def update_suite(self, source_module, mutant_module):
        source_module_shortname = source_module.__name__.split('.')[-1]
        if hasattr(self.suite_module, source_module_shortname):
            setattr(self.suite_module, source_module_shortname, mutant_module)
            self.suite = unittest.TestLoader().loadTestsFromModule(self.suite_module)
            return True
        return False

#
# class CustomImporter(object):
#
#     def __init__(self, module):
#         if "sample.calculator" in sys.modules:
#             del sys.modules["sample.calculator"]
#         self.module = module
#
#     def find_module(self, fullname, path=None):
#         """
#         This method is called by Python if this class is on sys.path.
#
#         fullname: the fully-qualified name of the module to look for
#         path: either __path__ (for submodules and subpackages) or None (for a top-level module/package).
#
#         Note that this method will be called every time an import
#         statement is detected (or __import__ is called), before
#         Python's built-in package/module-finding code kicks in.
#         """
#
#         if fullname == "sample.calculator":
#
#         # As per PEP #302 (which implemented the sys.meta_path protocol),
#         # if fullname is the name of a module/package that we want to
#         # report as found, then we need to return a loader object.
#         # In this simple example, that will just be self.
#
#             return self
#
#         # If we don't provide the requested module, return None, as per
#         # PEP #302.
#         return None
#
#     def load_module(self, fullname):
#         """
#         This method is called by Python if CustomImporter.find_module does not return None.
#         fullname is the fully-qualified name of the module/package that was requested.
#         """
#
#         if fullname != "sample.calculator":
#              # Raise ImportError as per PEP #302 if the requested module/package
#              # couldn't be loaded. This should never be reached in this
#              # simple example, but it's included here for completeness. :)
#              raise ImportError(fullname)
#
#         # PEP#302 says to return the module if the loader object (i.e,
#         # this class) successfully loaded the module.
#         # Note that a regular class works just fine as a module.
#         # self.module.__loader__ = self
#         # sys.modules[fullname] = self.module
#         return
#
#
# if __name__ == "__main__":
#
#     # load the module to test
#     target_module_name = "sample.calculator"
#     target_module = ModuleLoader.load_single_module(target_module_name)
#
#     # prepare test suite
#     sys.meta_path.insert(0, CustomImporter(target_module))
#
#     # load test suite module
#     suite_module_name = "sample.unittest_calculator"
#     suite_module = ModuleLoader.load_single_module(suite_module_name)
#
#     # run test
#     test_result = MuTester.run(suite_module, None)
#
#     print "Done!"
