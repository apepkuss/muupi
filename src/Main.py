from MuManager import *
from MuUtilities import *
from astdump import *
import codegen
import imp
import sys


if __name__ == "__main__":
    manager = MuManager()

    # load the module to mutate
    source_module_fullname = "sample.calculator"
    source_module_shortname = "calculator"
    source_module = ModuleLoader.load_single_module(source_module_fullname)

    # load the test module
    suite_module_name = "sample.unittest_calculator"
    suite_module = ModuleLoader.load_single_module(suite_module_name)

    # create an instance of MuTester
    tester = MuTester(suite_module)

    print "********** Run test suite on source file **********"

    # run a unit test suite on original sut
    test_result = tester.run()

    # todo: do further analysis on the test result

    # build mutation operators
    operators = ['AOR']
    mutation_operators = MutationOperator.build(operators)
    assert mutation_operators is not None

    # build ast
    mutator = ASTMutator()

    original_tree = mutator.parse(source_module)
    ast.fix_missing_locations(original_tree)

    print "********** Run test suite on mutants **********"
    # mutate the original tree
    operator = None
    for k, v in mutation_operators.iteritems():
        if k == ast.BinOp or k == ast.UnaryOp:
            for op in v:
                # mutate the original sut
                operator = (k, op)
                mutated_tree = mutator.mutate(operator)
                ast.fix_missing_locations(mutated_tree)

                # generate a mutant module from mutated ast tree
                mutant_module = generate_mutant_module(mutated_tree, source_module_shortname)

                # remove the source module from sys.modules
                # del sys.modules[source_module_fullname]

                if tester.update_suite(source_module, mutant_module):
                    test_result = tester.run()

                    # todo: do further analaysis on test result

            print "********** Mutation Test Done! **********\n"

        break
