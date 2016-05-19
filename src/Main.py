from MuManager import *
from MuUtilities import *
from astdump import *


if __name__ == "__main__":
    manager = MuManager()

    # load a module
    source_module_name = "sample.calculator"
    module_calculator = ModuleLoader.load_single_module(source_module_name)

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
                exec compile(mutated_tree, "<string>", "exec")

            print "********** Mutation Test Done! **********\n"
