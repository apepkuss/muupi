import unittest
import inspect
import codegen
import sys
import os
import ctypes
import multiprocessing
import collections

from MuUtilities import *
from multiprocessing import Process
from threading import Thread


class MuTester(multiprocessing.Process):

    def __init__(self):
        Process.__init__(self)
        self.mutated_module = None
        self.original_module = None
        self.test_suite_module = None
        self.test_suite = None
        self.mutated = False
        self.que = multiprocessing.Queue()

    def load_test_suite_module(self, test_suite_module):
        self.test_suite_module = test_suite_module
        # generate an instance of unittest.TestSuite
        self.test_suite = unittest.TestLoader().loadTestsFromModule(test_suite_module)

    def set_module_undert_test(self, module):
        self.original_module = module

    def set_mutant_module(self, mutated_module, original_module):
        self.mutated_module = mutated_module
        self.original_module = original_module
        self.mutated = True

    def run(self):
        if self.mutated:
            if not self.update_test_suite_module():
                print "Failed to update module before running test!"
                return

        self.test_suite = unittest.TestSuite()
        self.test_suite.addTests(unittest.findTestCases(self.test_suite_module))
        test_result = MutationTestResult()
        self.test_suite.run(test_result)
        self.que.put(test_result.serialize())

    def update_test_suite_module(self):
        source_module_shortname = self.original_module.__name__.split('.')[-1]
        if hasattr(self.test_suite_module, source_module_shortname):
            setattr(self.test_suite_module, source_module_shortname, self.mutated_module)
            return True
        return False

    def get_result(self, timeout=100):
        return self.que.get(timeout)


SerializedTestResult = collections.namedtuple(typename='SerializedTestResult', field_names=['testsRun', 'skipped', 'failures', 'errors'])


class MutationTestResult(unittest.TestResult):

    def serialize(self):
        failures = {}
        for failure in self.failures:
            failures[str(failure[0])] = failure[1]

        errors = {}
        for error in self.errors:
            errors[str(error[0])] = error[1]

        skipped = len(self.skipped)
        testsRun = self.testsRun - skipped

        return SerializedTestResult(testsRun=testsRun, skipped=skipped, failures=failures, errors=errors)

