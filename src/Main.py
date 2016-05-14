from MuManager import *
from MuUtilities import *
from astdump import *


if __name__ == "__main__":
    manager = MuManager()

    source_module_name = "sample.calculator"

    test_suite = None

    # load a module
    module_calculator = ModuleLoader.load_single_module(source_module_name)

    # build ast
    original_tree = AST.build_ast(module_calculator)
    ast.fix_missing_locations(original_tree)
    exec compile(original_tree, "<string>", "exec")

    visitor = ASTMutator()
    mutated_tree = visitor.visit(original_tree)
    ast.fix_missing_locations(mutated_tree)

    exec compile(mutated_tree, "<string>", "exec")

    # manager.setup(source_module_name, test_suite)
    # manager.perform()
    # manager.report()

    print "DONE."
