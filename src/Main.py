from MuManager import *
from MuUtilities import *
from astdump import *
import codegen
import imp


if __name__ == "__main__":
    manager = MuManager()

    # load the module to mutate
    source_module_name = "sample.calculator"
    module_calculator = ModuleLoader.load_single_module(source_module_name)

    # load the test module
    suite_module_name = "sample.unittest_calculator"
    suite_module = ModuleLoader.load_single_module(suite_module_name)


    # build mutation operators
    operators = ['AOR']
    mutation_operators = MutationOperator.build(operators)
    assert mutation_operators is not None

    # build ast
    mutator = ASTMutator()

    original_tree = mutator.parse(module_calculator)
    ast.fix_missing_locations(original_tree)
    print "\n********** Original AST **********"
    exec compile(original_tree, "<string>", "exec")

    # mutate the original tree
    operator = None
    for k, v in mutation_operators.iteritems():
        if k == ast.BinOp or k == ast.UnaryOp:
            for op in v:
                operator = (k, op)
                mutated_tree = mutator.mutate(operator)
                ast.fix_missing_locations(mutated_tree)
                print "********** Mutated AST **********"

                # generate a mutant module from mutated ast tree
                mutant_file_name = "mutant_filename"
                mutant_module_name = "mutant_modulename"
                mutant_module = generate_mutant_module(mutated_tree, mutant_file_name, mutant_module_name)

                # todo:
                mutated_source_code = codegen.to_source(mutated_tree)
                print mutated_source_code

                test_result = MuTester.run(suite_module=suite_module, module_to_test=mutant_module)
                print "test"

            print "********** Mutation Test Done! **********\n"
