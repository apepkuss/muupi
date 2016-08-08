from MutantGenerator import *
from MuUtilities import *
from MuOperators import *
from MuAnalyzer import *
from astdump import *
from collections import namedtuple

import multiprocessing as mp
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--module-fullname', type=str, default=None,
                        help='Full name of module under test.')
    parser.add_argument('-p', '--module-path', type=str, default=None,
                        help='The path of source code of module under test.')
    parser.add_argument('-M', '--tsmodule-fullname', type=str, default=None,
                        help='Full name of test suite module.')
    parser.add_argument('-P', '--tsmodule-path', type=str, default=None,
                        help='The path of source code of test suite module.')

    parsed_args = parser.parse_args(sys.argv[1:])
    return parsed_args, parser


def make_config(pargs, parser):
    pdict = pargs.__dict__
    return pdict


if __name__ == "__main__":

    # parsed_args, parser = parse_args()
    # config = make_config(parsed_args, parser)
    # print('Random testing using config={}'.format(config))

    # load target module
    print "Loading target module ...... "
    # todo: DO NOT REMOVE THE FOLLOWING TWO LINES
    module_under_test_fullname = "sample.avl"
    module_under_test_path = "../sample/avl.py"

    # module_under_test_fullname = config["module_fullname"]
    # module_under_test_path = config["module_path"]

    module_under_test = MuUtilities.load_module(module_under_test_fullname, module_under_test_path)
    print "Done.\n"

    # load test suite module
    print "Loading test suite module ...... "
    # todo: DO NOT REMOVE THE FOLLOWING TWO LINES
    suite_module_fullname = "sample.unittest_calculator"
    suite_module_path = "../sample/unittest_calculator.py"

    # suite_module_fullname = config["tsmodule_fullname"]
    # suite_module_path = config["tsmodule_path"]

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

    if False or len(test_result.failures) > 0 or len(test_result.errors) > 0:
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





