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
    parser.add_argument('-t', '--tsmodule-fullname', type=str, default=None,
                        help='Full name of test suite module.')
    parser.add_argument('-P', '--tsmodule-path', type=str, default=None,
                        help='The path of source code of test suite module.')
    parser.add_argument('-g', '--generator', type=str, default=None,
                        help='Specify a generator.')
    parser.add_argument('-l', '--list-generators', action='store_true',
                        help='List all available generators.')

    parsed_args = parser.parse_args(sys.argv[1:])
    return parsed_args, parser


def make_config(pargs, parser):
    # pdict = pargs.__dict__
    # return pdict

    pdict = pargs.__dict__
    # create a namedtuple object for fast attribute lookup
    key_list = pdict.keys()
    arg_list = [pdict[k] for k in key_list]
    Config = namedtuple('Config', key_list)
    nt_config = Config(*arg_list)
    return nt_config


def generator_factory(generator):
    if generator == "randomtester":
        randomtester = MuUtilities.load_module("generator.randomtester")
        return randomtester
    elif generator == "randombeam":
        return None
    elif generator == "bfsmodelchecker":
        return None
    elif generator == "dfsmodelchecker":
        return None
    elif generator == "choose for me":
        return None
    else:
        return None


if __name__ == "__main__":

    parsed_args, parser = parse_args()
    config = make_config(parsed_args, parser)
    # print('Random testing using config={}'.format(config))

    suite_module = None
    module_under_test = None

    if config.list_generators:
        print "TODO: list all available generators."

    # load module to mutate
    if config.module_fullname:
        print "Loading target module ...... "
        # todo: DO NOT REMOVE THE FOLLOWING TWO LINES
        # module_under_test_fullname = "sample.calculator"
        # module_under_test_path = "../sample/calculator.py"

        module_under_test_fullname = config.module_fullname
        module_under_test_path = config.module_path

        module_under_test = MuUtilities.load_module(module_under_test_fullname, module_under_test_path)
        assert module_under_test is not None
        print "Done.\n"

        print "Loading mutation operators ...... "
        # build mutation operators
        operators = None #['ZIL']
        mutation_operators = MutationOperator.build(operators)
        assert len(mutation_operators) > 0
        print "Done.\n"

        # DEBUG: print out the abstract syntax tree of target module
        # print_ast(original_tree)

        # generate mutants from target module
        print "Generating mutants from target module ...... "
        # mutants = MutantGenerator().mutate(module=module_under_test, operators=mutation_operators)
        print "Done.\n"

        if config.generator:
            # todo: load a specified generator, e.g. randomtester, randombeam, bfsmodelchecker, and etc.
            # suite_module = generator_factory(config.generator)

            # load test suite module
            if suite_module is None:
                if config.tsmodule_fullname is None:
                    print "Specify the fullname of test suite module:"
                    config.tsmodule_fullname = input()

                print "Loading test suite module ...... "
                # todo: DO NOT REMOVE THE FOLLOWING TWO LINES
                # suite_module_fullname = "sample.unittest_calculator"
                # suite_module_path = "../sample/unittest_calculator.py"

                suite_module_fullname = config.tsmodule_fullname
                suite_module_path = config.tsmodule_path

                suite_module = MuUtilities.load_module(suite_module_fullname, suite_module_path)
                print "Done.\n"

            # run a unit test suite on original sut
            print "Running unit test cases against target module before mutation ......"
            tester = MuTester()
            tester.load_test_suite_module(suite_module)
            tester.start()
            test_result = tester.get_result()
            tester.terminate()
            print "Test runs: " + str(test_result.testsRun) \
                  + "; failures: " + str(len(test_result.failures)) \
                  + "; errors: " + str(len(test_result.errors))
            print "Done.\n"

            # if False or len(test_result.failures) > 0 or len(test_result.errors) > 0:
            #     print "Warning: current module to mutate failed in current unit test."
            # else:

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





