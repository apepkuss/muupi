import ast
import config
import copy
import sys
from MuUtilities import *
from copy import deepcopy

##### for test ########
from MuUtilities import *
import codegen


#######################


class MutationOperator(object):
    @classmethod
    def type(cls):
        return cls.__class__

    @classmethod
    def build(cls, names=None):
        if names is None or len(names) == 0:
            names = ['AOD', 'AOR', 'ASR', 'BCR', 'LOD', 'LOI', 'CRP', 'CDL', \
                     'EXS', 'LCR', 'BOD', 'BOR', 'FHD', 'FCD', 'OIL', 'RIL', \
                     'COR', 'SSIR', 'SEIR', 'STIR', 'SVD', 'SMD', 'ZIL']

        cls.mutation_operators = []

        for name in names:
            if name == 'AOD':
                # if ast.UnaryOp not in cls.mutation_operators:
                #     cls.mutation_operators[ast.UnaryOp] = [ArithmeticOperatorDeletion]
                # elif ArithmeticOperatorDeletion not in cls.mutation_operators[ast.UnaryOp]:
                #     cls.mutation_operators[ast.UnaryOp].append(ArithmeticOperatorDeletion)
                cls.mutation_operators.append((ast.UnaryOp, ArithmeticOperatorDeletion))

            if name == 'AOR':
                cls.mutation_operators.append((ast.BinOp, ArithmeticOperatorReplacement))
                cls.mutation_operators.append((ast.UnaryOp, ArithmeticOperatorReplacement))

            if name == 'ASR':
                cls.mutation_operators.append((ast.AugAssign, AssignmentOperatorReplacement))

            if name == 'BCR':
                cls.mutation_operators.append((ast.Break, BreakContinueReplacement))
                cls.mutation_operators.append((ast.Continue, BreakContinueReplacement))

            if name == 'LOD':
                cls.mutation_operators.append((ast.UnaryOp, LogicalOperatorDeletion))

            if name == 'LOI':
                cls.mutation_operators.append((ast.UnaryOp, LogicalOperatorInsertion))
                cls.mutation_operators.append((ast.BoolOp, LogicalOperatorInsertion))

            if name == 'CRP':
                cls.mutation_operators.append((ast.Num, ConstantReplacement))
                cls.mutation_operators.append((ast.Str, ConstantReplacement))

            if name == 'CDL':
                cls.mutation_operators.append((ast.List, ConstantDeletion))
                # cls.mutation_operators.append((ast.Str, ConstantDeletion))

            if name == 'EXS':
                cls.mutation_operators.append((ast.ExceptHandler, ExceptionSwallowing))

            if name == 'LCR':
                cls.mutation_operators.append((ast.UnaryOp, LogicalConnectorReplacement))
                cls.mutation_operators.append((ast.BoolOp, LogicalConnectorReplacement))

            if name == 'BOD':
                cls.mutation_operators.append((ast.UnaryOp, BitwiseOperatorDeletion))

            if name == 'BOR':
                cls.mutation_operators.append((ast.BitAnd, BitwiseOperatorReplacement))
                cls.mutation_operators.append((ast.BitOr, BitwiseOperatorReplacement))
                cls.mutation_operators.append((ast.BitXor, BitwiseOperatorReplacement))
                cls.mutation_operators.append((ast.LShift, BitwiseOperatorReplacement))
                cls.mutation_operators.append((ast.RShift, BitwiseOperatorReplacement))

            if name == 'FHD':
                cls.mutation_operators.append((ast.TryFinally, FinallyHandlerDeletion))

            if name == 'OIL':
                cls.mutation_operators.append((ast.While, OneIterationLoop))
                cls.mutation_operators.append((ast.For, OneIterationLoop))

            if name == 'RIL':
                cls.mutation_operators.append((ast.For, ReverseIterationLoop))

            if name == 'COR':
                cls.mutation_operators.append((ast.Eq, ComparisonOperatorReplacement))
                cls.mutation_operators.append((ast.NotEq, ComparisonOperatorReplacement))
                cls.mutation_operators.append((ast.Lt, ComparisonOperatorReplacement))
                cls.mutation_operators.append((ast.Gt, ComparisonOperatorReplacement))
                cls.mutation_operators.append((ast.LtE, ComparisonOperatorReplacement))
                cls.mutation_operators.append((ast.GtE, ComparisonOperatorReplacement))


            if name == 'SSIR':
                cls.mutation_operators.append((ast.Slice, SliceStartIndexDeletion))

            if name == 'SEIR':
                cls.mutation_operators.append((ast.Slice, SliceEndIndexDeletion))

            if name == 'STIR':
                cls.mutation_operators.append((ast.Slice, SliceStepIndexDeletion))

            if name == 'SVD':
                cls.mutation_operators.append((ast.Attribute, SelfVariableDeletion))

            if name == 'ZIL':
                cls.mutation_operators.append((ast.For, ZeroIterationLoop))
                cls.mutation_operators.append((ast.While, ZeroIterationLoop))

            if name == 'SMD':
                cls.mutation_operators.append((ast.Raise, StatementDeletion))
                cls.mutation_operators.append((ast.Call, StatementDeletion))
                cls.mutation_operators.append((ast.Expr, StatementDeletion))
                cls.mutation_operators.append((ast.Assign, StatementDeletion))
                cls.mutation_operators.append((ast.AugAssign, StatementDeletion))
                cls.mutation_operators.append((ast.Pass, StatementDeletion))

        return cls.mutation_operators

    @classmethod
    def list_all_operators(cls):
        res = []

        res.append((ArithmeticOperatorDeletion.name(), ArithmeticOperatorDeletion.__name__))
        res.append((ArithmeticOperatorReplacement.name(), ArithmeticOperatorReplacement.__name__))
        res.append((AssignmentOperatorReplacement.name(), AssignmentOperatorReplacement.__name__))
        res.append((BreakContinueReplacement.name(), BreakContinueReplacement.__name__))
        res.append((LogicalOperatorDeletion.name(), LogicalOperatorDeletion.__name__))

        res.append((LogicalOperatorInsertion.name(), LogicalOperatorInsertion.__name__))
        res.append((LogicalConnectorReplacement.name(), LogicalConnectorReplacement.__name__))
        res.append((BitwiseOperatorDeletion.name(), BitwiseOperatorDeletion.__name__))
        res.append((BitwiseOperatorReplacement.name(), BitwiseOperatorReplacement.__name__))
        res.append((ConstantReplacement.name(), ConstantReplacement.__name__))

        res.append((FinallyHandlerDeletion.name(), FinallyHandlerDeletion.__name__))
        res.append((ExceptionSwallowing.name(), ExceptionSwallowing.__name__))
        res.append((ComparisonOperatorReplacement.name(), ComparisonOperatorReplacement.__name__))
        res.append((SliceStartIndexDeletion.name(), SliceStartIndexDeletion.__name__))
        res.append((SliceEndIndexDeletion.name(), SliceEndIndexDeletion.__name__))

        res.append((SliceStepIndexDeletion.name(), SliceStepIndexDeletion.__name__))
        res.append((OneIterationLoop.name(), OneIterationLoop.__name__))
        res.append((ReverseIterationLoop.name(), ReverseIterationLoop.__name__))
        res.append((SelfVariableDeletion.name(), SelfVariableDeletion.__name__))
        res.append((ZeroIterationLoop.name(), ZeroIterationLoop.__name__))

        res.append((StatementDeletion.name(), StatementDeletion.__name__))

        return res


class ArithmeticOperatorDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return 'AOD'

    @classmethod
    def mutate(cls, node):
        """
        mutate unary +, -
        """
        if node not in config.visited_nodes:
            if node.__class__ is ast.UnaryOp:
                if node.op.__class__ is ast.USub or node.op.__class__ is ast.UAdd:
                    config.mutated = True
                    original_node = deepcopy(node)
                    parent = config.parent_dict[node]
                    del config.parent_dict[node]
                    node = node.operand
                    config.parent_dict[node] = parent
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node

        return node


class ArithmeticOperatorReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return 'AOR'

    @classmethod
    def mutate(cls, node):
        """
        mutate binary operators:
            1. mathematical operators: +, -, *, /, %, **
            2. bitwise operators:  >>, <<, |, &, ^
        """
        if node not in config.visited_nodes:
            if node.__class__ is ast.BinOp:

                if node.op.__class__ is ast.Add:
                    if node.left.__class__ in [ast.Str, ast.List] or node.right.__class__ in [ast.Str, ast.List]:
                        return node

                if node.op.__class__ in config.arithmetic_operators:
                    config.arithmetic_operators.remove(node.op.__class__)

                while len(config.arithmetic_operators) > 0:

                    original_node = deepcopy(node)
                    parent = config.parent_dict[node]
                    del config.parent_dict[node]

                    op_node = None
                    op_type = config.arithmetic_operators.pop()
                    if op_type is ast.Add:
                        op_node = ast.Add()
                    elif op_type is ast.Sub:
                        op_node = ast.Sub()
                    elif op_type is ast.Mult:
                        op_node = ast.Mult()
                    elif op_type is ast.Div:
                        op_node = ast.Div()
                    elif op_type is ast.FloorDiv:
                        op_node = ast.FloorDiv()
                    else:
                        print "TypeError in AOR"
                    if op_node:
                        node.op = op_node
                        config.parent_dict[node] = parent
                        config.node_pairs[node] = original_node
                        config.current_mutated_node = node
                        config.mutated = True
                        return node

                if len(config.arithmetic_operators) == 0:
                    config.arithmetic_operators = [ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv]
                    config.visited_nodes.add(node)

            elif node.__class__ is ast.UnaryOp:
                if node.op.__class__ is ast.UAdd:
                    config.mutated = True
                    original_node = deepcopy(node)
                    parent = config.parent_dict[node]
                    del config.parent_dict[node]
                    node.op = ast.USub()
                    config.parent_dict[node] = parent
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node

                elif node.op.__class__ is ast.USub:
                    config.mutated = True
                    original_node = deepcopy(node)
                    parent = config.parent_dict[node]
                    del config.parent_dict[node]
                    node.op = ast.UAdd()
                    config.parent_dict[node] = parent
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node

                    # todo: try more unary operations

        return node


class AssignmentOperatorReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "ASR"

    @classmethod
    def mutate(cls, node):
        """
        mutate assignment operator
            1. += to -=
            2. -= to +=
            3. *= to /=
            4. /= to *=
            5. //= to /=
        """
        if node not in config.visited_nodes:
            if node.__class__ is ast.AugAssign:

                if node.op.__class__ is ast.Add:
                    if node.value.__class__ is ast.Str and node.value.__class__ is ast.Call and hasattr(node.value.func, 'id') and node.value.func.id == 'str':
                        return node

                if node.op.__class__ in config.arithmetic_operators:
                    config.arithmetic_operators.remove(node.op.__class__)

                while len(config.arithmetic_operators) > 0:

                    original_node = deepcopy(node)
                    parent = config.parent_dict[node]
                    del config.parent_dict[node]

                    op_node = None
                    op_type = config.arithmetic_operators.pop()
                    if op_type is ast.Add:
                        op_node = ast.Add()
                    elif op_type is ast.Sub:
                        op_node = ast.Sub()
                    elif op_type is ast.Mult:
                        op_node = ast.Mult()
                    elif op_type is ast.Div:
                        op_node = ast.Div()
                    elif op_type is ast.FloorDiv:
                        op_node = ast.FloorDiv()
                    else:
                        print "TypeError in ASR"
                    if op_node:
                        node.op = op_node
                        config.parent_dict[node] = parent
                        config.node_pairs[node] = original_node
                        config.current_mutated_node = node
                        config.mutated = True
                        return node

                if len(config.arithmetic_operators) == 0:
                    config.arithmetic_operators = [ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv]
                    config.visited_nodes.add(node)

        return node


class BitwiseOperatorDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "BOD"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.UnaryOp and node.op.__class__ is ast.Invert:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node = node.operand
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class BitwiseOperatorReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "BOR"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.BitAnd:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node = ast.BitOr()
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

            elif node.__class__ is ast.BitOr:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node = ast.BitAnd()
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

            elif node.__class__ is ast.BitXor:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node = ast.BitAnd()
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

            elif node.__class__ is ast.LShift:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node = ast.RShift()
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

            elif node.__class__ is ast.RShift:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node = ast.LShift()
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class BreakContinueReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "BCR"

    @classmethod
    def mutate(cls, node):
        """
        Mutate break and continue statements
            1. break to continue
            2. continue to break
        """
        if node not in config.visited_nodes:
            if node.__class__ is ast.Break:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node = ast.Continue()
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

            elif node.__class__ is ast.Continue:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node = ast.Break()
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class ConstantReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "CRP"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.Num:
                config.mutated = True
                original_node = deepcopy(node)
                node.n += 1
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

            elif node.__class__ is ast.Str and len(node.s) > 0:
                config.mutated = True
                original_node = deepcopy(node)
                node.s = ''
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class ConstantDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "CDL"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes and node.__class__ in [ast.List, ast.Set, ast.Tuple]:
            if len(node.elts) > 0:
                i = 0
                while i < len(node.elts):
                    if node.elts[i] not in config.visited_nodes:
                        break
                    i += 1
                if i == len(node.elts):
                    config.visited_nodes.add(node)
                else:
                    original_node = node.elts[i]
                    node.elts.remove(original_node)
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node
                    config.mutated = True
        return node


class LogicalOperatorDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "LOD"

    @classmethod
    def mutate(cls, node):
        """
        remove 'not' operator
        """
        if node not in config.visited_nodes:
            if node.__class__ is ast.UnaryOp and node.op.__class__ is ast.Not:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node = node.operand
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class LogicalOperatorInsertion(MutationOperator):
    @classmethod
    def name(cls):
        return "LOI"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if config.parent_dict[node].__class__ in [ast.If, ast.While, ast.IfExp, ast.Assert]:
                if node.__class__ is ast.UnaryOp:
                    config.mutated = True
                    original_node = deepcopy(node)
                    parent = config.parent_dict[node]
                    del config.parent_dict[node]
                    node = node.operand
                    config.parent_dict[node] = parent
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node

                elif node.__class__ is ast.BoolOp:
                    config.mutated = True
                    original_node = deepcopy(node)
                    parent = config.parent_dict[node]
                    del config.parent_dict[node]
                    unary_op_node = ast.UnaryOp()
                    unary_op_node.op = ast.Not()
                    unary_op_node.operand = node
                    node = unary_op_node
                    config.parent_dict[node] = parent
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node

        return node


class LogicalConnectorReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "LCR"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.BoolOp:
                if node.op.__class__ is ast.And:
                    config.mutated = True
                    original_node = deepcopy(node)
                    node.op = ast.Or()
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node

                elif node.op.__class__ is ast.Or:
                    config.mutated = True
                    original_node = deepcopy(node)
                    node.op = ast.And()
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node

        return node


class StatementDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "SMD"

    @classmethod
    def mutate(cls, node):
        """
        Replace raise, break, continue with pass.
        """
        if node not in config.visited_nodes:
            if node.__class__ in [ast.Raise, ast.Assign, ast.AugAssign, ast.Call, ast.Expr, ast.Pass] and node in config.nodes_to_remove:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                config.nodes_to_remove.remove(node)
                node = ast.Pass()
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


# class ExceptionHandlerDeletion(MutationOperator):
#     @classmethod
#     def name(cls):
#         return "EHD"
#
#     @classmethod
#     def mutate(cls, node):
#         # if node.__class__ is ast.ExceptHandler:
#         if node.__class__ is ast.ExceptHandler:
#             config.mutated = True
#             node = None
#         return node


class FinallyHandlerDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "FHD"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.TryFinally:
                config.mutated = True
                original_node = deepcopy(node)
                node.finalbody = [ast.Pass()]
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class ExceptionSwallowing(MutationOperator):
    @classmethod
    def name(cls):
        return "EXS"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.ExceptHandler:
                config.mutated = True
                original_node = deepcopy(node)
                node.body = [ast.Pass()]
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class ComparisonOperatorReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "COR"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ in [ast.Eq, ast.NotEq, ast.Lt, ast.Gt, ast.LtE, ast.GtE]:
                if node.__class__ in config.comparison_operators:
                    config.comparison_operators.remove(node.__class__)

                while len(config.comparison_operators) > 0:

                    original_node = deepcopy(node)
                    parent = config.parent_dict[node]
                    del config.parent_dict[node]

                    node_type = config.comparison_operators.pop()
                    if node_type is ast.Eq:
                        node = ast.Eq()
                    elif node_type is ast.NotEq:
                        node = ast.NotEq()
                    elif node_type is ast.Lt:
                        node = ast.Lt()
                    elif node_type is ast.Gt:
                        node = ast.Gt()
                    elif node_type is ast.LtE:
                        node = ast.LtE()
                    elif node_type is ast.GtE:
                        node = ast.GtE()
                    else:
                        print "TypeError in AOR"

                    config.parent_dict[node] = parent
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node
                    config.mutated = True
                    return node

                if len(config.arithmetic_operators) == 0:
                    config.arithmetic_operators = [ast.Eq, ast.NotEq, ast.Lt, ast.Gt, ast.LtE, ast.GtE]
                    config.visited_nodes.add(node)

        return node


class SliceStartIndexDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "SSIR"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.Slice and node.lower is not None:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node.lower = None
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class SliceEndIndexDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "SEIR"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.Slice and node.upper is not None:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node.upper = None
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node
        return node


class SliceStepIndexDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "STIR"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.Slice and node.step is not None:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node.step = None
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node
        return node


class OneIterationLoop(MutationOperator):
    @classmethod
    def name(cls):
        return "OIL"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ in [ast.While, ast.For]:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node.body.append(ast.Break())
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class ReverseIterationLoop(MutationOperator):
    @classmethod
    def name(cls):
        return "RIL"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.For and node.iter is not None:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                mutated_node = ast.Call(func=ast.Name(id='reversed', ctx=ast.Load()), args=[node.iter], keywords=[],
                                        starargs=None, kwargs=None)
                node.iter = mutated_node
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


class SelfVariableDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "SVD"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ is ast.Attribute:
                if node.value.__class__ is ast.Name and node.value.id == 'self':
                    config.mutated = True
                    original_node = deepcopy(node)
                    parent = config.parent_dict[node]
                    del config.parent_dict[node]
                    node = ast.Name(node.attr, node.ctx)
                    config.parent_dict[node] = parent
                    config.node_pairs[node] = original_node
                    config.current_mutated_node = node

        return node


class ZeroIterationLoop(MutationOperator):
    @classmethod
    def name(cls):
        return "ZIL"

    @classmethod
    def mutate(cls, node):
        if node not in config.visited_nodes:
            if node.__class__ in [ast.For, ast.While]:
                config.mutated = True
                original_node = deepcopy(node)
                parent = config.parent_dict[node]
                del config.parent_dict[node]
                node.body = [ast.Break()] + node.body
                config.parent_dict[node] = parent
                config.node_pairs[node] = original_node
                config.current_mutated_node = node

        return node


###################### todo: another 8 rules to be added ############################

class DecoratorDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "DDL"

    @classmethod
    def mutate(cls, node):
        if node not in config.node_pairs:
            if node.__class__ is ast.FunctionDef and len(node.decorator_list) > 0:
                config.mutated = True
                config.node_pairs.add(node)
                node.decorator_list = []
        return node


class ClassmethodDecoratorInsertion(MutationOperator):
    @classmethod
    def name(cls):
        return "CDI"

    @classmethod
    def mutate(cls, node):
        pass


class HidingVariableDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "IHD"

    @classmethod
    def mutate(cls, node):
        pass


class OverridingMethodDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "IOD"

    @classmethod
    def mutate(cls, node):
        pass


class OverriddenMethodCallingPositionChange(MutationOperator):
    @classmethod
    def name(cls):
        return "IOP"

    @classmethod
    def mutate(cls, node):
        pass


class StaticmethodDecoratorInsertion(MutationOperator):
    @classmethod
    def name(cls):
        return "SDI"

    @classmethod
    def mutate(cls, node):
        pass


class SuperCallingDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "SCD"

    @classmethod
    def mutate(cls, node):
        pass


class SuperCallingInsertion(MutationOperator):
    @classmethod
    def name(cls):
        return "SCI"

    @classmethod
    def mutate(cls, node):
        pass
