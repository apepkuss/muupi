from MuManager import *
from MuUtilities import *
from MuOperators import *
from astdump import *


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

    if len(test_result.failures) > 0 or len(test_result.errors) > 0:
        print "The original test cases failed in test."

    else:
        # compute the total number of test cases
        total_test_cases = test_result.testsRun

        print "\n\n********** Phase 2: mutate target module with mutation operators and run test **********\n"
        # build mutation operators
        operators = ['AOR']
        mutation_operators = MutationOperator.build(operators)
        assert mutation_operators is not None
        print "Loading mutation operators ...... Done.\n"

        # build ast of target module
        mutator = ASTMutator()
        original_tree = mutator.parse(module_under_test)
        print "\nParsing abstract syntax tree ...... Done.\n"

        # DEBUG: print out the abstract syntax tree of target module
        # print_ast(original_tree)

        # number of killed mutants
        mutant_killed = 0
        # total number of mutants
        mutant_total = 0
        failures = []
        for operator in mutation_operators.iteritems():

            print "\n********** Step 1: mutate target module **********\n"
            # mutate the original sut
            mutant_module = mutator.mutate(operator)
            mutant_total += 1

            # diff two ast
            make_diff(mutator.original_ast, mutator.mutated_ast)

            print "\n********** Step 2: run test suite on mutated module **********\n"
            if tester.update_suite(module_under_test, mutant_module):
                test_result = tester.run()
                total_test_cases += test_result.testsRun
                if test_result.failures is not None and len(test_result.failures) > 0:
                    failures += [failure[0] for failure in test_result.failures]
                    mutant_killed += 1

        mutation_score = mutant_killed * 1.0 / mutant_total
        print "\n\nmutation score: " + str(mutation_score)
        print "\n\n********** Mutation Test Done! **********\n"
