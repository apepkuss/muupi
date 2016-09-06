import ast
import config
import imp
import logging

from MuUtilities import *
from copy import deepcopy
from MuOperators import StatementDeletion



class MutantGenerator(ast.NodeTransformer):
    def __init__(self):
        self.nodes_to_mutate = {}
        self.nodes_to_remove = set()
        self.nodes_to_potential = set()
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
                original_ast = ast.parse(code, filename=module_file.name)
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
        for operator in operators:

            # make a copy of the original ast for mutation
            original_ast_copy = deepcopy(self.original_ast)

            config.mutated = False

            # mutate the original sut
            self.mutated_ast = self.mutate_bySingleOperator(original_ast_copy, operator)
            # print codegen.to_source(self.mutated_ast)

            # generate a mutant module from mutated ast tree
            if config.mutated:
                mutated_module = self.generate_mutant_module(self.mutated_ast, operator[1].name()+'_'+operator[0].__name__)
                mutated_modules.append(mutated_module)

                # todo: diff two ast
                MuUtilities.make_diff(self.original_ast, self.mutated_ast, operator[1].name()+'_'+operator[0].__name__)

        return mutated_modules

    def mutate_bySingleOperator(self, tree, operator):
        """
        Mutate an abstract syntax tree by a single mutation operator
        :param tree: the target module to mutate
        :param operator: pre-defined mutation operator
        :return: a mutated abstract syntax tree
        """
        self.operator = operator

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
        try:
            exec mutant_code in mutant_module.__dict__
        except TypeError:
            print 'checkpoint'
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

    def visit_Num(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Str(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_UAdd(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_USub(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_BitAnd(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_BitOr(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_BitXor(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_LShift(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_RShift(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_And(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Or(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Attribute(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Compare(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_UnaryOp(self, node):
        """
        Visit and mutate a unary operation
        """
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_BinOp(self, node):
        """
        Visit and mutate a binary operation
        """
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_If(self, node):
        """
        Visit and mutate if-statement
        :param node:
        :return:
        """
        if self.operator[1] is StatementDeletion:
            for anode in node.body:
                if anode.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call]:
                    self.nodes_to_remove.add(anode)
                elif anode.__class__ in [ast.Expr]:
                    self.nodes_to_potential.add(anode)
            node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
        else:
            node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Expr(self, node):
        if self.operator[1] is StatementDeletion:
            if node in self.nodes_to_remove:
                node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
            elif node in self.nodes_to_potential:
                if node.value.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call]:
                    self.nodes_to_potential.remove(node)
                    self.nodes_to_remove.add(node)
                    node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
        else:
            node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_IfExp(self, node):
        """
        Visit and mutate if expression
        :param node:
        :return:
        """
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Assert(self, node):
        """
        Visit and mutate if expression
        :param node:
        :return:
        """
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_For(self, node):
        if self.operator[1] is StatementDeletion:
            for anode in node.body:
                if anode.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call]:
                    self.nodes_to_remove.add(anode)
                elif anode.__class__ in [ast.Expr]:
                    self.nodes_to_potential.add(anode)
            node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
        else:
            node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_While(self, node):
        if self.operator[1] is StatementDeletion:
            for anode in node.body:
                if anode.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call]:
                    self.nodes_to_remove.add(anode)
                elif anode.__class__ in [ast.Expr]:
                    self.nodes_to_potential.add(anode)
            node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
        else:
            node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Break(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Continue(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Raise(self, node):
        if self.operator[1] is StatementDeletion:
            if len(self.nodes_to_remove) > 0 and node in self.nodes_to_remove:
                node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
        else:
            node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Assign(self, node):
        if self.operator[1] is StatementDeletion:
            if len(self.nodes_to_remove) > 0 and node in self.nodes_to_remove:
                node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
        else:
            node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_AugAssign(self, node):
        if self.operator[1] is StatementDeletion:
            if len(self.nodes_to_remove) > 0 and node in self.nodes_to_remove:
                node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
        else:
            node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_Slice(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_TryFinally(self, node):
        node = self.mutate_single_node(node, self.operator)
        if node:
            self.dfs_visit(node)
        return node

    # def visit_TryExcept(self, node):
    #     node = self.mutate_single_node(node, self.operator)
    #     if node:
    #         self.dfs_visit(node)
    #     return node

    def visit_ExceptHandler(self, node):
        node = self.mutate_single_node(node, self.operator)
        if node:
            self.dfs_visit(node)
        return node

    def visit_Call(self, node):
        if self.operator[1] is StatementDeletion:
            if len(self.nodes_to_remove) > 0 and node in self.nodes_to_remove:
                node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
        else:
            node = self.mutate_single_node(node, self.operator)
        if node:
            self.dfs_visit(node)
        return node

    def visit_FunctionDef(self, node):
        if self.operator[1] is StatementDeletion:
            for anode in node.body:
                if anode.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call]:
                    self.nodes_to_remove.add(anode)
                elif anode.__class__ in [ast.Expr]:
                    self.nodes_to_potential.add(anode)
            node = self.mutate_single_node(node, self.operator, self.nodes_to_remove)
        else:
            node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    def visit_ClassDef(self, node):
        node = self.mutate_single_node(node, self.operator)
        self.dfs_visit(node)
        return node

    # def mutate_single_node(self, node, operator):
    #     """
    #     Mutate a single node by a specified operator
    #     """
    #     if node.__class__ is operator[0]:
    #         # mutate
    #         mutated_node = operator[1].mutate(node)
    #
    #         if config.mutated:
    #             node = mutated_node
    #
    #     return node

    def mutate_single_node(self, node, operator, nodes_to_remove=None):
        """
        Mutate a single node by a specified operator
        """
        if node.__class__ is operator[0]:
            # mutate
            if nodes_to_remove:
                mutated_node = operator[1].mutate(node, nodes_to_remove)
            else:
                mutated_node = operator[1].mutate(node)

            if config.mutated:
                node = mutated_node

        return node


