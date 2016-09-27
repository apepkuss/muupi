import ast
import config
import imp
import logging

from MuUtilities import *
from copy import deepcopy
from MuOperators import StatementDeletion

from timethis import timefunc
from timethis import timeblock

class MutantGenerator(ast.NodeTransformer):
    def __init__(self):
        self.nodes_to_mutate = {}
        # self.nodes_to_remove = set()
        # self.nodes_to_potential = set()
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

    @timefunc
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
        config.counter = 0
        for operator in operators:

            # initialize global variables
            config.nodes_to_remove = set()
            config.nodes_to_potential = set()
            config.node_pairs = {}
            config.visited_nodes = set()
            config.current_mutated_node = None
            config.parent_dict = {}

            # make a copy of the original ast for mutation
            original_ast_copy = deepcopy(self.original_ast)
            # print codegen.to_source(original_ast_copy)

            # while config.mutated:
            while True:
                config.mutated = False

                # mutate the original sut
                self.mutated_ast = self.mutate_bySingleOperator(original_ast_copy, operator)
                # print codegen.to_source(self.mutated_ast)

                if not config.mutated:
                    break

                # generate a mutant module from mutated ast tree
                mutated_module = self.generate_mutant_module(self.mutated_ast, operator[1].name()+'_'+operator[0].__name__)
                mutated_modules.append(mutated_module)

                MuUtilities.output(self.original_ast, self.mutated_ast, operator[1].name() + '_' + operator[0].__name__)

                # recover
                self.mutated_ast = self.rollback_mutation(self.mutated_ast, operator)
                # print codegen.to_source(self.mutated_ast)

        return mutated_modules

    def mutate_bySingleOperator(self, root, operator):
        """
        Mutate an abstract syntax tree by a single mutation operator
        :param root: the target module to mutate
        :param operator: pre-defined mutation operator
        :return: a mutated abstract syntax tree
        """
        self.operator = operator

        ast.fix_missing_locations(root)
        # traverse the target ast tree and mutate interesting node
        mutated_ast = self.visit(root)
        ast.fix_missing_locations(root)

        return mutated_ast

    def rollback_mutation(self, root, operator):
        config.recovering = True
        return self.mutate_bySingleOperator(root, operator)

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

    def mutate_single_node(self, node, operator):
        """
        Mutate a single node by a specified operator
        """
        if node.__class__ is operator[0] or (operator[1] is StatementDeletion and node.__class__ is ast.Pass):
            mutated_node = operator[1].mutate(node)
            node = mutated_node

        return node

    def visit_node(self, node):
        if node and not config.mutated:
            for child in ast.iter_child_nodes(node):
                config.parent_dict[child] = node
            node = self.mutate_single_node(node, self.operator)

            if node and not config.mutated:
                self.dfs_visit(node)
        return node

    def recover_node(self, node):
        if node and config.mutated and config.recovering:
            if node == config.current_mutated_node:
                if hasattr(node, 'lineno'):
                    print str(node.lineno)

                original_node = config.node_pairs[node]

                if self.operator[1] is ConstantDeletion:
                    node.elts.append(original_node)

                    del config.node_pairs[node]
                    config.visited_nodes.add(original_node)
                    config.recovering = False

                else:
                    if node in config.parent_dict:
                        parent = config.parent_dict[node]
                    else:
                        print "KeyError in " + node.lineno

                    del config.parent_dict[node]
                    del config.node_pairs[node]

                    node = original_node
                    config.parent_dict[original_node] = parent

                    if self.operator[1] not in [ArithmeticOperatorReplacement, AssignmentOperatorReplacement, ComparisonOperatorReplacement, ConstantReplacement] or \
                            (self.operator[1] in [ArithmeticOperatorReplacement, ConstantReplacement] and original_node.__class__ not in [ast.BinOp, ast.Num]):
                        config.visited_nodes.add(original_node)
                    config.recovering = False

            else:
                self.dfs_visit(node)
        return node

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

    # Literals

    def visit_Num(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Str(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_List(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Tuple(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Set(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Dict(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    # Variables

    def visit_Name(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    # Expressions

    def visit_Expr(self, node):
        if node and not config.mutated:
            for child in ast.iter_child_nodes(node):
                config.parent_dict[child] = node

            if self.operator[1] is StatementDeletion:
                if node in config.nodes_to_remove:
                    node = self.mutate_single_node(node, self.operator)
                elif node in config.nodes_to_potential:
                    if node.value.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call]:
                        config.nodes_to_potential.remove(node)
                        config.nodes_to_remove.add(node)
                        node = self.mutate_single_node(node, self.operator)
            else:
                node = self.mutate_single_node(node, self.operator)
            if node and not config.mutated:
                self.dfs_visit(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_UnaryOp(self, node):
        """
        Visit and mutate a unary operation
        """
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_UAdd(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_USub(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_BinOp(self, node):
        """
        Visit and mutate a binary operation
        """
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_BitAnd(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_BitOr(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_BitXor(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_LShift(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_RShift(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_BoolOp(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_And(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Or(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Compare(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Eq(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_NotEq(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Lt(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Gt(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_LtE(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_GtE(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Is(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_IsNot(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_In(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_NotIn(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Call(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_IfExp(self, node):
        """
        Visit and mutate if expression
        :param node:
        :return:
        """
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Attribute(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    # Scripting

    def visit_Index(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Slice(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Subscript(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    # Statements

    def visit_Assign(self, node):
        if node and not config.mutated:
            for child in ast.iter_child_nodes(node):
                config.parent_dict[child] = node

            if self.operator[1] is StatementDeletion:
                if len(config.nodes_to_remove) > 0 and node in config.nodes_to_remove:
                    node = self.mutate_single_node(node, self.operator)
            else:
                node = self.mutate_single_node(node, self.operator)
            if node and not config.mutated:
                self.dfs_visit(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_AugAssign(self, node):
        if node and not config.mutated:
            for child in ast.iter_child_nodes(node):
                config.parent_dict[child] = node

            if self.operator[1] is StatementDeletion:
                if len(config.nodes_to_remove) > 0 and node in config.nodes_to_remove:
                    node = self.mutate_single_node(node, self.operator)
            else:
                node = self.mutate_single_node(node, self.operator)
            if node and not config.mutated:
                self.dfs_visit(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Print(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Raise(self, node):
        if node and not config.mutated:
            for child in ast.iter_child_nodes(node):
                config.parent_dict[child] = node

            if self.operator[1] is StatementDeletion:
                if len(config.nodes_to_remove) > 0 and node in config.nodes_to_remove:
                    node = self.mutate_single_node(node, self.operator)
            else:
                node = self.mutate_single_node(node, self.operator)
            if node and not config.mutated:
                self.dfs_visit(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Assert(self, node):
        """
        Visit and mutate if expression
        :param node:
        :return:
        """
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Pass(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    # Control Flow

    def visit_If(self, node):
        """
        Visit and mutate if-statement
        :param node:
        :return:
        """
        if node and not config.mutated:
            for child in ast.iter_child_nodes(node):
                config.parent_dict[child] = node

            if self.operator[1] is StatementDeletion:
                for anode in node.body:
                    if anode.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call] and anode not in config.nodes_to_remove:
                        config.nodes_to_remove.add(anode)
                    elif anode.__class__ in [ast.Expr] and anode not in config.nodes_to_remove:
                        config.nodes_to_potential.add(anode)
                node = self.mutate_single_node(node, self.operator)
            else:
                node = self.mutate_single_node(node, self.operator)
            if node and not config.mutated:
                self.dfs_visit(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_For(self, node):
        if node and not config.mutated:
            for child in ast.iter_child_nodes(node):
                config.parent_dict[child] = node

            if self.operator[1] is StatementDeletion:
                for anode in node.body:
                    if anode.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call]:
                        config.nodes_to_remove.add(anode)
                    elif anode.__class__ in [ast.Expr]:
                        config.nodes_to_potential.add(anode)
                node = self.mutate_single_node(node, self.operator)
            else:
                node = self.mutate_single_node(node, self.operator)
            if node and not config.mutated:
                self.dfs_visit(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_While(self, node):
        if node and not config.mutated:
            for child in ast.iter_child_nodes(node):
                config.parent_dict[child] = node

            if self.operator[1] is StatementDeletion:
                for anode in node.body:
                    if anode.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call]:
                        config.nodes_to_remove.add(anode)
                    elif anode.__class__ in [ast.Expr]:
                        config.nodes_to_potential.add(anode)
                node = self.mutate_single_node(node, self.operator)
            else:
                node = self.mutate_single_node(node, self.operator)
            if node and not config.mutated:
                self.dfs_visit(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Break(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Continue(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_TryFinally(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_TryExcept(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_ExceptHandler(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_With(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    # Comprehensions
    def visit_ListComp(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_SetComp(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_GeneratorExp(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_DictComp(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    # Function and class definitions

    def visit_Return(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_arguments(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_Lambda(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node

    def visit_FunctionDef(self, node):
        if node and not config.mutated:
            for child in ast.iter_child_nodes(node):
                config.parent_dict[child] = node

            if self.operator[1] is StatementDeletion:
                for anode in node.body:
                    if anode.__class__ in [ast.Raise, ast.Continue, ast.Break, ast.Assign, ast.AugAssign, ast.Call]:
                        config.nodes_to_remove.add(anode)
                    elif anode.__class__ in [ast.Expr]:
                        config.nodes_to_potential.add(anode)

            node = self.mutate_single_node(node, self.operator)

            if node and not config.mutated:
                self.dfs_visit(node)
                # print codegen.to_source(node)

        elif node and config.mutated and config.recovering:
            return self.recover_node(node)

        return node

    def visit_ClassDef(self, node):
        if node and not config.mutated:
            return self.visit_node(node)
        elif node and config.mutated and config.recovering:
            return self.recover_node(node)
        return node




