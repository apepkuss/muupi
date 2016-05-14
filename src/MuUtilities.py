import importlib
import ast
from MuOperators import *


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


class AST(object):

    @classmethod
    def build_ast(cls, module):
        """
        Build an abstract syntax tree from a source file
        """
        with open(module.__file__) as module_file:
            return ast.parse(module_file.read(), module_file.name)

    @classmethod
    def mutate_ast(cls):
        """
        Mutate all interesting nodes on the ast of the target module
        """
        pass

    @classmethod
    def mutate_single_node(cls, node):
        """
        Mutate a single interesting node on the ast of the target module
        """
        pass


class ASTMutator(ast.NodeTransformer):

    def __init__(self):
        self.nodes_to_mutate = {}

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

    @dfs_ast
    def visit_BinOp(self, node):
        """
        Visit and mutate a binary operation
        """

        if node.op.__class__ is ast.Add:
            if ast.Add not in self.nodes_to_mutate:
                self.nodes_to_mutate[ast.Add] = [node]
            else:
                self.nodes_to_mutate[ast.Add].append(node)

            # mutate
            # mutated_node = ast.BinOp(left=node.left, op=ast.Sub(), right=node.right)
            mutated_node = self.mutate_single_node(node, ArithmeticOperatorReplacement)

            # sample code: mutate Add to Subtract
            return mutated_node

        return node

    def mutate_single_node(self, node, operator):

        if node.__class__ is ast.BinOp and node.op.__class__ is ast.Add:
            if operator.__name__ == 'ArithmeticOperatorReplacement':
                return ast.BinOp(left=node.left, op=ast.Sub(), right=node.right)



    @dfs_ast
    def visit_FunctionDef(self, node):

        if ast.FunctionDef not in self.nodes_to_mutate:
            self.nodes_to_mutate[ast.FunctionDef] = [(node.name, node)]
        else:
            self.nodes_to_mutate[ast.FunctionDef].append((node.name, node))

        return node

    @dfs_ast
    def visit_ClassDef(self, node):

        if ast.ClassDef not in self.nodes_to_mutate:
            self.nodes_to_mutate[ast.ClassDef] = [(node.name, node)]
        else:
            self.nodes_to_mutate[ast.ClassDef].append((node.name, node))

        return node


if __name__ == "__main__":
    source_module_name = "sample.calculator"

    # load a module
    module_calculator = ModuleLoader.load_single_module(source_module_name)

    # build ast
    original_tree = AST.build_ast(module_calculator)
    ast.fix_missing_locations(original_tree)
    exec compile(original_tree, "<TiP>", "exec")

    visitor = ASTMutator()
    mutated_tree = visitor.visit(original_tree)
    ast.fix_missing_locations(mutated_tree)

    exec compile(mutated_tree, "<TiP>", "exec")

    # tree = ast.parse("a + b")
    # ast.fix_missing_locations(tree)
    # print ast.dump(tree)
    #
    # tree = ASTMutator().visit(tree)
    # ast.fix_missing_locations(tree)
    # print ast.dump(tree)
