from MuManager import *
from MuUtilities import *
from astdump import *


if __name__ == "__main__":
    manager = MuManager()

    source_module_name = "sample.calculator"

    test_suite = None

    # load a module
    module_calculator = ModuleLoader.load_single_module(source_module_name)

    tree = AST.build_ast(module_calculator)
    print tree
    AST.parse_ast()
    print AST.class_nodes
    print AST.function_nodes

    for node in AST.class_nodes:
        print node[0]

    for node in AST.function_nodes:
        print node[0]




    # manager.setup(source_module_name, test_suite)
    # manager.perform()
    # manager.report()

    print "DONE."
