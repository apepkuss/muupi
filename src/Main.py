from MuManager import *
from MuUtilities import *
from MuOperators import *
from astdump import *
from copy import deepcopy

import codegen
import imp
import sys


if __name__ == "__main__":
    manager = MuManager()

    # load target module
    module_under_test_fullname = "sample.calculator"
    module_under_test_shortname = "calculator"
    module_under_test = ModuleLoader.load_single_module(module_under_test_fullname)

    # load test suite module
    suite_module_name = "sample.unittest_calculator"
    suite_module = ModuleLoader.load_single_module(suite_module_name)

    # create an instance of MuTester
    tester = MuTester(suite_module)

    print "\n\n********** Phase 1: run test suite on target module **********\n"

    # run a unit test suite on original sut
    test_result = tester.run()

    # todo: do further analysis on the test result

    print "\n\n********** Phase 2: mutate target module with mutation operators and run test **********\n"
    # build mutation operators
    operators = ['AOR']
    mutation_operators = MutationOperator.build(operators)
    assert mutation_operators is not None

    # build ast of target module
    mutator = ASTMutator()
    original_tree = mutator.parse(module_under_test)

    # print out the abstract syntax tree of target module
    code = codegen.to_source(original_tree)
    print code

    ast.fix_missing_locations(original_tree)

    # mutate the original tree
    operator = None
    mutator_dict = {}
    for operator in mutation_operators.iteritems():

        # make a copy of the original ast for mutation
        original_tree_copy = deepcopy(original_tree)

        print "\n********** Step 1: mutate target module **********\n"
        # mutate the original sut
        mutant_module = mutator.mutate(operator)

        # remove the source module from sys.modules
        # del sys.modules[source_module_fullname]

        print "\n********** Step 2: run test suite on mutated module **********\n"
        if tester.update_suite(module_under_test, mutant_module):
            test_result = tester.run()

    print "********** Mutation Test Done! **********\n"
