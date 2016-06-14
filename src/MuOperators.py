import ast

##### for test ########
from MuUtilities import *
import codegen
#######################


class MutationOperator(object):

    @classmethod
    def type(cls):
        return cls.__class__

    @classmethod
    def build(cls, names):
        if names == []: return None

        cls.mutation_operators = {}
        for name in names:
            if name == 'AOD':
                if ast.UnaryOp not in cls.mutation_operators:
                    cls.mutation_operators[ast.UnaryOp] = [ArithmeticOperatorDeletion]
                else:
                    cls.mutation_operators[ast.UnaryOp].append(ArithmeticOperatorDeletion)

            if name == 'AOR':
                if ast.UnaryOp not in cls.mutation_operators:
                    cls.mutation_operators[ast.UnaryOp] = [ArithmeticOperatorReplacement]
                else:
                    cls.mutation_operators[ast.UnaryOp].append(ArithmeticOperatorReplacement)

                if ast.BinOp not in cls.mutation_operators:
                    cls.mutation_operators[ast.BinOp] = [ArithmeticOperatorReplacement]
                else:
                    cls.mutation_operators[ast.BinOp].append(ArithmeticOperatorReplacement)

            if name == 'ASR':
                if ast.AugAssign not in cls.mutation_operators:
                    cls.mutation_operators[ast.AugAssign] = [AssignmentOperatorReplacement]
                else:
                    cls.mutation_operators[ast.AugAssign].append(AssignmentOperatorReplacement)

            if name == 'BCR':
                if ast.Break not in cls.mutation_operators:
                    cls.mutation_operators[ast.Break] = [BreakContinueReplacement]
                else:
                    cls.mutation_operators[ast.Break].append(BreakContinueReplacement)

                if ast.Continue not in cls.mutation_operators:
                    cls.mutation_operators[ast.Continue] = [BreakContinueReplacement]
                else:
                    cls.mutation_operators[ast.Continue].append(BreakContinueReplacement)

            if name == 'COD':
                if ast.If not in cls.mutation_operators:
                    cls.mutation_operators[ast.If] = [ConditionalOperatorDeletion]
                else:
                    cls.mutation_operators[ast.If].append(ConditionalOperatorDeletion)

            if name == 'COI':
                if ast.If not in cls.mutation_operators:
                    cls.mutation_operators[ast.If] = [ConditionalOperatorInsertion]
                else:
                    cls.mutation_operators[ast.If].append(ConditionalOperatorInsertion)

            if name == 'CRP':
                if ast.Assign not in cls.mutation_operators:
                    cls.mutation_operators[ast.Assign] = [ConstantReplacement]
                else:
                    cls.mutation_operators[ast.Assign].append(ConstantReplacement)

            if name == 'LCR':
                if ast.If not in cls.mutation_operators:
                    cls.mutation_operators[ast.If] = [LogicalConnectorReplacement]
                else:
                    cls.mutation_operators[ast.If].append(LogicalConnectorReplacement)

            if name == 'LOD':
                if ast.UnaryOp not in cls.mutation_operators:
                    cls.mutation_operators[ast.UnaryOp] = [LogicalOperatorDeletion]
                else:
                    cls.mutation_operators[ast.UnaryOp].append(LogicalOperatorDeletion)

            if name == 'LOR':
                if ast.BinOp not in cls.mutation_operators:
                    cls.mutation_operators[ast.BinOp] = [LogicalOperatorReplacement]
                else:
                    cls.mutation_operators[ast.BinOp].append(LogicalOperatorReplacement)

            if name == 'OIL':
                if ast.For not in cls.mutation_operators:
                    cls.mutation_operators[ast.For] = [OneIterationLoop]
                else:
                    cls.mutation_operators[ast.For].append(OneIterationLoop)

                if ast.While not in cls.mutation_operators:
                    cls.mutation_operators[ast.While] = [OneIterationLoop]
                else:
                    cls.mutation_operators[ast.While].append(OneIterationLoop)

        return cls.mutation_operators


class ArithmeticOperatorDeletion(MutationOperator):

    @classmethod
    def name(cls):
        return 'AOD'

    @classmethod
    def mutate(cls, node):
        """
        mutate unary +, -, not
        """
        if node.op.__class__ is ast.USub or node.op.__class__ is ast.UAdd:
            return node.operand

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

        if node.__class__ is ast.BinOp:
            # mutate arithmetic +, -, *, /, %, pow(), >>, <<, |, &, ^
            if node.op.__class__ is ast.Add:
                return ast.BinOp(left=node.left, op=ast.Sub(), right=node.right)
            if node.op.__class__ is ast.Sub:
                return ast.BinOp(left=node.left, op=ast.Add(), right=node.right)
            if node.op.__class__ is ast.Mult:
                return ast.BinOp(left=node.left, op=ast.Div(), right=node.right)
            if node.op.__class__ is ast.Div:
                return ast.BinOp(left=node.left, op=ast.Mult(), right=node.right)
            if node.op.__class__ is ast.FloorDiv:
                return ast.BinOp(left=node.left, op=ast.Div(), right=node.right)
            if node.op.__class__ is ast.Mod:
                # return ast.BinOp(left=node.left, op=ast.Div(), right=node.right)
                pass
            if node.op.__class__ is ast.Pow:
                # return ast.BinOp(left=node.left, op=ast.Div(), right=node.right)
                pass
            if node.op.__class__ is ast.LShift:
                # return ast.BinOp(left=node.left, op=ast.Div(), right=node.right)
                pass
            if node.op.__class__ is ast.RShift:
                # return ast.BinOp(left=node.left, op=ast.Div(), right=node.right)
                pass
            if node.op.__class__ is ast.BitOr:
                # return ast.BinOp(left=node.left, op=ast.Div(), right=node.right)
                pass
            if node.op.__class__ is ast.BitXor:
                # return ast.BinOp(left=node.left, op=ast.Div(), right=node.right)
                pass
            if node.op.__class__ is ast.BitAnd:
                # return ast.BinOp(left=node.left, op=ast.Div(), right=node.right)
                pass

            # todo: try more binary operations

            return node

        if node.__class__ is ast.UnaryOp:
            if node.op.__class__ is ast.UAdd:
                return ast.UnaryOp(op=ast.USub(), operand=node.operand)
            if node.op.__class__ is ast.USub:
                return ast.UnaryOp(op=ast.UAdd(), operand=node.operand)

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
        if node.op.__class__ is ast.Add:
            return ast.AugAssign(target=node.target, op=ast.Sub(), value=node.value)
        if node.op.__class__ is ast.Sub:
            return ast.AugAssign(target=node.target, op=ast.Add(), value=node.value)
        if node.op.__class__ is ast.Mult:
            return ast.AugAssign(target=node.target, op=ast.Div(), value=node.value)
        if node.op.__class__ is ast.Div:
            return ast.AugAssign(target=node.target, op=ast.Mult(), value=node.value)
        if node.op.__class__ is ast.FloorDiv:
            return ast.AugAssign(target=node.target, op=ast.Div(), value=node.value)

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
        if node.__class__ is ast.Break:
            return ast.Break()
        if node.__class__ is ast.Continue:
            return ast.Continue()


class ConditionalOperatorDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "COD"

    @classmethod
    def mutate(cls, node):
        """
        remove bitwise invert operator: ~
        """
        if node.__class__ is ast.If and node.test.__class__ is ast.UnaryOp:
            if node.test.op.__class__ is ast.Not:
                node.test = node.test.operand
                return node
        return None


class ConditionalOperatorInsertion(MutationOperator):
    @classmethod
    def name(cls):
        return "COI"

    @classmethod
    def mutate(cls, node):

        if node.__class__ is ast.If and node.test.__class__ is ast.Compare:
            unary_op_node = ast.UnaryOp()
            unary_op_node.op = ast.Not()
            unary_op_node.operand = node.test
            unary_op_node.lineno = node.test.lineno
            unary_op_node.col_offset = node.test.col_offset
            node.test = unary_op_node
            return node
        return None


class LogicalConnectorReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "LCR"

    @classmethod
    def mutate(cls, node):

        if node.__class__ is ast.If and node.test.__class__ is ast.BoolOp:
            if node.test.op.__class__ is ast.And:
                node.test.op = ast.Or()
                return node
            if node.test.op.__class__ is ast.Or:
                node.test.op = ast.And()
                return node
        return None


class LogicalOperatorDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "LOD"

    @classmethod
    def mutate(cls, node):

        if node.__class__ is ast.UnaryOp and node.op.__class__ is ast.Invert:
            return node.operand

        return node


class LogicalOperatorReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "LOR"

    @classmethod
    def mutate(cls, node):

        if node.__class__ is ast.BinOp:
            if node.op.__class__ is ast.BitAnd:
                return ast.BinOp(left=node.left, op=ast.BitOr(), right=node.right)
            if node.op.__class__ is ast.BitOr:
                return ast.BinOp(left=node.left, op=ast.BitAnd(), right=node.right)
            if node.op.__class__ is ast.BitXor:
                return ast.BinOp(left=node.left, op=ast.BitAnd(), right=node.right)
            if node.op.__class__ is ast.LShift:
                return ast.BinOp(left=node.left, op=ast.RShift(), right=node.right)
            if node.op.__class__ is ast.RShift:
                return ast.BinOp(left=node.left, op=ast.LShift(), right=node.right)
        return node


class ConstantReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "CRP"

    @classmethod
    def mutate(cls, node):

        if node.__class__ is ast.Assign:
            if node.value.__class__ is ast.Num and hasattr(node.value, 'n'):
                original_value = getattr(node.value, 'n')
                setattr(node.value, 'n', original_value+1)
                return node
            elif node.value.__class__ is ast.Str and hasattr(node.value, 's'):
                setattr(node.value, 's', '')
                return node
        return None


class DecoratorDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "DDL"

    @classmethod
    def mutate(cls, node):
        pass


class ExceptionHandlerDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "EHD"

    @classmethod
    def mutate(cls, node):
        pass


class ExceptionSwallowing(MutationOperator):
    @classmethod
    def name(cls):
        return "EXS"

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





class RelationalOperatorReplacement(MutationOperator):
    @classmethod
    def name(cls):
        return "ROR"

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


class SliceIndexRemove(MutationOperator):
    @classmethod
    def name(cls):
        return "SIR"

    @classmethod
    def mutate(cls, node):
        pass


class ClassmethodDecoratorInsertion(MutationOperator):
    @classmethod
    def name(cls):
        return "CDI"

    @classmethod
    def mutate(cls, node):
        pass


class OneIterationLoop(MutationOperator):
    @classmethod
    def name(cls):
        return "OIL"

    @classmethod
    def mutate(cls, node):

        if node.__class__ is ast.While:
            node.body.append(ast.Break())

        elif node.__class__ is ast.For:
            node.body.append(ast.Break())

        return node


class ReverseIterationLoop(MutationOperator):
    @classmethod
    def name(cls):
        return "RIL"

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


class StatementDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "SDL"

    @classmethod
    def mutate(cls, node):
        pass


class SelfVariableDeletion(MutationOperator):
    @classmethod
    def name(cls):
        return "SVD"

    @classmethod
    def mutate(cls, node):
        pass


class ZeroIterationLoop(MutationOperator):
    @classmethod
    def name(cls):
        return "ZIL"

    @classmethod
    def mutate(cls, node):
        pass


if __name__ == "__main__":
    # load the module to mutate
    source_module_fullname = "sample.calculator"
    source_module_shortname = "calculator"
    source_module = ModuleLoader.load_single_module(source_module_fullname)

    # build mutation operators
    operators = ['OIL']
    mutation_operators = MutationOperator.build(operators)
    assert mutation_operators is not None

    # build ast
    mutator = ASTMutator()

    original_tree = mutator.parse(source_module)
    ast.fix_missing_locations(original_tree)

    # mutate the original tree
    operator = None
    mutator_dict = {}
    for operator in mutation_operators.iteritems():
        #if operator[0] == ast.UnaryOp:  # or k == ast.UnaryOp:

        # mutate the original sut
        mutated_tree = mutator.mutate(operator)
        ast.fix_missing_locations(mutated_tree)

        # print out the mutated tree
        code = codegen.to_source(mutated_tree)
        print code



    print "********** Operator Test Done! **********\n"
