from MutantGenerator import *
from MuUtilities import *
from MuOperators import *
from MuAnalyzer import *
from astdump import *
import multiprocessing as mp

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
    tester = MuTester()
    tester.load_test_suite_module(suite_module)
    tester.start()
    test_result = tester.get_result()
    tester.terminate()
    print "Done.\n"

    if len(test_result.failures) > 0 or len(test_result.errors) > 0:
        print "Warning: current module to mutate failed in current unit test."

    else:
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

        testers = []
        for mutant in mutants:
            tester = MuTester()
            tester.load_test_suite_module(suite_module)
            tester.set_mutant_module(mutated_module=mutant, original_module=module_under_test)
            testers.append(tester)

        results = []
        for tester in testers:
            tester.start()
            # results.append(tester.get_result())
            # tester.terminate()

        for tester in testers:
            tester.join()
            results.append(tester.get_result())

        # analyze test results
        print "Computing mutation score ......"
        MuAnalyzer.analyze(results)
        print "Done.\n"

        print "\n\n********** Mutation Test Done! **********\n"
