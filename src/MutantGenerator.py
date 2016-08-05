import ast
import imp
from MuUtilities import *

from copy import deepcopy


class MutantGenerator(ast.NodeTransformer):

    def __init__(self):
        self.nodes_to_mutate = {}
        self.original_ast = None
        self.mutated_ast = None

        # operator is a dict
        self.operator = None

    def set_mutation_operators(self, mutation_operators):
        self.operator = mutation_operators

    def parse(self, module):
        """
        Build an abstract syntax tree from a target module.
        :param module: target module to parse
        :return: an abstract syntax tree
        """
        original_ast = None
        with open(module.__file__) as module_file:
            try:
                code = module_file.read()
                original_ast = ast.parse(code, module_file.name)
            except TypeError:
                # remove the pyc file of sut if raise a TypeError exception
                pass
        assert original_ast is not None
        return original_ast

    def mutate(self, module, operators):
        """
        Mutate a target module with specified mutation operators
        :param module: the target module to mutate
        :param operators: mutation oeprators
        :return: a list of mutated modules
        """

        # generate ast from target module
        self.original_ast = self.parse(module)

        mutated_modules = []
        for operator in operators.iteritems():

            print "\n********** Step 1: mutate target module **********\n"

            # make a copy of the original ast for mutation
            original_ast_copy = deepcopy(self.original_ast)

            # mutate the original sut
            self.mutated_ast = self.mutate_bySingleOperator(original_ast_copy, operator)
            # generate a mutant module from mutated ast tree
            mutated_modules.append(self.generate_mutant_module(self.mutated_ast))

            # todo: diff two ast
            MuUtilities.make_diff(self.original_ast, self.mutated_ast)

        return mutated_modules

    def mutate_bySingleOperator(self, tree, operator):
        """
        Mutate an abstract syntax tree by a single mutation operator
        :param tree: the target module to mutate
        :param operator: pre-defined mutation operator
        :return: a mutated abstract syntax tree
        """
        self.operator = operator

        # ast.fix_missing_locations(original_ast_copy)
        ast.fix_missing_locations(tree)
        # traverse the target ast tree and mutate interesting node
        mutated_ast = self.visit(tree)
        ast.fix_missing_locations(tree)

        return mutated_ast

    def generate_mutant_module(self, mutated_ast, module_shortname=""):
        """
        Generate a module from a mutated ast
        :param mutated_ast: the mutated ast
        :param module_shortname: the short name of the module mutated
        :return: an mutated module
        """
        prefix = "mutant_"
        mutant_module_shortname = prefix + module_shortname
        mutant_code = compile(mutated_ast, mutant_module_shortname, "exec")
        mutant_module = imp.new_module(mutant_module_shortname)
        exec mutant_code in mutant_module.__dict__
        return mutant_module

    def dfs_visit(self, node):
        """
        Parse a node's children
        """
        super(MutantGenerator, self).generic_visit(node)

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

    def visit_Attribute(self, node):

        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break
            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)
                return mutated_node

        self.dfs_visit(node)
        return node

    def visit_Compare(self, node):

        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break
            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)
                return mutated_node

        self.dfs_visit(node)
        return node

    def visit_UnaryOp(self, node):
        """
        Visit and mutate a unary operation
        """
        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break
            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)
                return mutated_node

        self.dfs_visit(node)
        return node

    def visit_BinOp(self, node):
        """
        Visit and mutate a binary operation
        """
        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break
            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)
                return mutated_node

        self.dfs_visit(node)
        return node

    def visit_If(self, node):
        """
        Visit and mutate if-statement
        :param node:
        :return:
        """
        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break

            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)
                return mutated_node
        self.dfs_visit(node)
        return node

    def visit_For(self, node):

        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break

            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)
                return mutated_node

        self.dfs_visit(node)
        return node

    def visit_While(self, node):

        if node.__class__ is self.operator[0]:

            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break

            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)
                return mutated_node
        self.dfs_visit(node)
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
                self.dfs_visit(mutated_node)

        self.dfs_visit(node)
        return node

    def visit_Slice(self, node):
        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break

            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)

        self.dfs_visit(node)
        return node

    def visit_ExceptHandler(self, node):

        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break
            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)

        self.dfs_visit(node)
        return node

    def visit_FunctionDef(self, node):

        if node.__class__ is self.operator[0]:
            mutated_node = None
            for operator_class in self.operator[1]:
                # mutate
                mutated_node = self.mutate_single_node(node, operator_class)
                if mutated_node is not None:
                    break
            if mutated_node is not None:
                # visit child nodes
                self.dfs_visit(mutated_node)

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
