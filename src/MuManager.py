from MuAnalyzer import *
from MutantGenerator import *
from MuTester import *

import codegen


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

        # load the module to mutate
        source_module_fullname = "sample.calculator"
        source_module_shortname = "calculator"
        source_module = MuUtilities.load_single_module(source_module_fullname)

        # build mutation operators
        operators = ['RIL']
        mutation_operators = MutationOperator.build(operators)
        assert mutation_operators is not None

        # build ast
        mutator = ASTMutator()

        original_tree = mutator.parse(source_module)
        # # print out the original tree
        # code = codegen.to_source(original_tree)
        # print code
        ast.fix_missing_locations(original_tree)

        # mutate the original tree
        operator = None
        mutator_dict = {}
        for operator in mutation_operators.iteritems():
            # mutate the original sut
            mutated_tree = mutator.mutate_bySingleOperator(operator)
            ast.fix_missing_locations(mutated_tree)

            # print out the mutated tree
            code = codegen.to_source(mutated_tree)
            print code
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
