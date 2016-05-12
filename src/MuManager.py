from MuAnalyzer import *
from MutantGenerator import *
from MuTester import *


class MuManager(object):

    def __init__(self):
        self.mutant_generator = None
        self.tester = None
        self.source = None
        self.suite = None
        self.analyzer = None

    def setup(self, source_module, test_suite):
        """
        Makes all preparations for the future testing
        """
        self.source = source_module
        self.suite = test_suite

        self.mutant_generator = MutantGenerator()
        self.tester = MuTester()
        self.analyzer = MuAnalyzer()

        pass

    def perform(self):
        """
        Performs a mutation testing
        """
        # step1: tester runs the test suite on the original source module
        original_result = self.tester.run(self.suite, self.sut)

        # step2: mutant_generator mutates the source module according to the specified mutators.
        #        By default, use all mutators
        mutant = self.mutant_generator.generate(self.source)

        # step3: tester runs the test suite on the mutated source module.
        mutant_result = self.tester.run(self.suite, mutant)

        # step4: analyzer analyzes test results, computes mutation scores, and makes a final report
        self.analyzer.analyze(mutant_result)
        pass

    def report(self):
        """
        Reports the final result after running a test suite on a target mutant
        """
        self.analyzer.report()
        pass
