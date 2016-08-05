from MuManager import *
from MuUtilities import *
from MuOperators import *
from astdump import *



if __name__ == "__main__":

    # load target module
    print "Loading target module ...... "
    module_under_test_fullname = "sample.calculator"
    module_under_test_path = "../sample/calculator.pyc"
    module_under_test = MuUtilities.load_module(module_under_test_fullname, module_under_test_path)
    print "Done.\n"

    # load test suite module
    print "Loading test suite module ...... "
    suite_module_fullname = "sample.unittest_calculator"
    suite_module_path = "../sample/unittest_calculator.pyc"
    suite_module = MuUtilities.load_module(suite_module_fullname, suite_module_path)
    print "Done.\n"

    # run a unit test suite on original sut
    print "Running unit test cases against target module before mutation ......"
    tester = MuTester(suite_module)
    test_result = tester.run()
    print "Done.\n"

    if len(test_result.failures) > 0 or len(test_result.errors) > 0:
        print "Warning: current module to mutate failed in current unit test."

    else:
        # compute the total number of test cases
        total_test_cases = test_result.testsRun

        print "Loading mutation operators ...... "
        # build mutation operators
        operators = ['AOR']
        mutation_operators = MutationOperator.build(operators)
        assert mutation_operators is not None
        print "Done.\n"

        # DEBUG: print out the abstract syntax tree of target module
        # print_ast(original_tree)

        # generate mutants from target module
        print "Generating mutants from target module ...... "
        mutants = MutantGenerator().mutate(module=module_under_test, operators=mutation_operators)
        print "Done.\n"

        # run test cases against mutated modules
        print "Running test cases against mutants ...... "
        results = []
        for mutant in mutants:
            if tester.update_suite(module_under_test, mutant):
                results.append(tester.run())
        print "Done.\n"

        # analyze test results
        print "Computing mutation score ......"
        MuAnalyzer.analyze(results)
        print "Done.\n"

        print "\n\n********** Mutation Test Done! **********\n"
