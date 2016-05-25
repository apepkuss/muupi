import imp
import importlib
from MuOperators import *
from MuTester import *


class ModuleLoader(object):

    @classmethod
    def load_modules(cls, full_module_names):
        """
        Load multiple modules by full module names
        """
        modules = []
        for name in full_module_names:
            module = cls.load_single_module(name)
            if module:
                modules.append(module)
        return modules

    @classmethod
    def load_single_module(cls, full_module_name):
        """
        Load a single module by full module name
        """
        module = None
        try:
            module = importlib.import_module(full_module_name)
        except ImportError:
            pass
        return module

    @classmethod
    def load_single_class(cls, full_class_string):
        """
        Loading dynamically a class with importlib is easy,
        first you have to actually load the module with import_module,
        and finally you can retrieve the class with getattr.
        """
        class_data = full_class_string.split(".")
        module_path = ".".join(class_data[:-1])
        class_str = class_data[-1]

        module = importlib.import_module(module_path)

        # Finally, we retrieve the Class
        return getattr(module, class_str)


class ASTMutator(ast.NodeTransformer):

    def __init__(self):
        self.nodes_to_mutate = {}
        self.original_ast = None

        # operator is a dict
        self.operator = None

    def set_mutation_operators(self, mutation_operators):
        self.operator = mutation_operators

    def parse(self, module):
        """
        Build an abstract syntax tree from a source file
        Return an AST tree
        """
        with open(module.__file__) as module_file:
            try:
                code = module_file.read()
                self.original_ast = ast.parse(code, module_file.name)
            except TypeError:
                # remove the pyc file of sut if raise a TypeError exception
                pass
        assert self.original_ast is not None
        return self.original_ast

    def mutate(self, operator):
        """
        Mutate an abstract syntax tree by a single mutation operator
        """
        self.operator = operator

        # traverse the target ast tree
        mutated_ast = self.visit(self.original_ast)

        return mutated_ast

    def dfs_visit(self, node):
        """
        Parse a node's children
        """
        super(ASTMutator, self).generic_visit(node)

    # todo: to be removed
    def dfs_ast(func):
        """
        decorator to make visitor work recursive
        """
        def wrapper(self, node):
            new_node = func(self, node)
            for child in ast.iter_child_nodes(new_node):
                self.visit(child)
            return new_node

        return wrapper

    def visit_UnaryOp(self, node):
        """
        Visit and mutate a unary operation
        """
        if node.__class__ is self.operator[0]:
            # mutate
            mutated_node = self.mutate_single_node(node, self.operator[1])
            assert mutated_node is not None

            # visit child nodes
            self.dfs_visit(mutated_node)

            # sample code: mutate Add to Subtract
            return mutated_node
        return node

    def visit_BinOp(self, node):
        """
        Visit and mutate a binary operation
        """
        if node.__class__ is self.operator[0]:
            # mutate
            mutated_node = self.mutate_single_node(node, self.operator[1])
            assert mutated_node is not None

            # visit child nodes
            self.dfs_visit(mutated_node)

            # sample code: mutate Add to Subtract
            return mutated_node
        return node

    def visit_If(self, node):
        """
        Visit and mutate if-statement
        :param node:
        :return:
        """
        if node.__class__ is self.operator[0]:

            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break
            assert mutated_node is not None

            # visit child nodes
            self.dfs_visit(mutated_node)

            return mutated_node
        return node

    def visit_Assign(self, node):

        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break

            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(node)

        return node

    def visit_For(self, node):

        # visit child nodes
        self.dfs_visit(node)

        return node

    def visit_FunctionDef(self, node):

        # if ast.FunctionDef not in self.nodes_to_mutate:
        #     self.nodes_to_mutate[ast.FunctionDef] = [(node.name, node)]
        # else:
        #     self.nodes_to_mutate[ast.FunctionDef].append((node.name, node))

        # visit child nodes
        self.dfs_visit(node)

        return node

    def visit_ClassDef(self, node):

        # if ast.ClassDef not in self.nodes_to_mutate:
        #     self.nodes_to_mutate[ast.ClassDef] = [(node.name, node)]
        # else:
        #     self.nodes_to_mutate[ast.ClassDef].append((node.name, node))

        # visit child nodes
        self.dfs_visit(node)

        return node

    def mutate_single_node(self, node, operator):
        """
        Mutate a single node by a specified operator
        """
        return operator.mutate(node)


def generate_mutant_module(mutated_ast, module_shortname):
    """
    generate a mutant module from a mutated ast
    """
    prefix = "mutant_"
    mutant_module_shortname = prefix + module_shortname
    mutant_code = compile(mutated_ast, mutant_module_shortname, "exec")
    mutant_module = imp.new_module(mutant_module_shortname)
    exec mutant_code in mutant_module.__dict__
    return mutant_module


if __name__ == "__main__":

    # PART I: test code

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
    operators = ['AOD', 'AOR', 'ASR']
    mutation_operators = MutationOperator.build(operators)
    assert mutation_operators is not None

    # build ast
    mutator = ASTMutator()

    original_tree = mutator.parse(source_module)
    ast.fix_missing_locations(original_tree)

    print "********** Run test suite on mutants **********"
    # mutate the original tree
    operator = None
    mutator_dict = {}
    for k, v in mutation_operators.iteritems():
        if k == ast.Assign:  # or k == ast.UnaryOp:
            for op in v:
                operator = (k, op)

                # mutate the original sut
                mutated_tree = mutator.mutate(operator)
                ast.fix_missing_locations(mutated_tree)

                # generate a mutant module from mutated ast tree
                mutant_module = generate_mutant_module(mutated_tree, source_module_shortname)

                # remove the source module from sys.modules
                # del sys.modules[source_module_fullname]

                if tester.update_suite(source_module, mutant_module):
                    test_result = tester.run()

                    # todo: do further analysis on test result

            print "********** Mutation Test Done! **********\n"

        break



    # # build ast
    # original_tree = AST.build_ast(module_calculator)
    # ast.fix_missing_locations(original_tree)
    # exec compile(original_tree, "<TiP>", "exec")
    #
    # visitor = ASTMutator()
    # mutated_tree = visitor.visit(original_tree)
    # ast.fix_missing_locations(mutated_tree)
    #
    # exec compile(mutated_tree, "<TiP>", "exec")

    # # PART II: test code
    # tree = ast.parse("+a")
    # ast.fix_missing_locations(tree)
    # print ast.dump(tree)
    #
    # tree = ASTMutator().visit(tree)
    # ast.fix_missing_locations(tree)
    # print ast.dump(tree)
