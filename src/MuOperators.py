import ast


class MutationOperator(object):

    @classmethod
    def type(cls):
        return cls.__class__

    @classmethod
    def build(cls, names):
        if names == []: return None

        cls.mutation_operators = {ast.UnaryOp: [], ast.BinOp: [], ast.AugAssign: []}
        for name in names:
            if name == 'AOD':
                cls.mutation_operators[ast.UnaryOp].append(ArithmeticOperatorDeletion)
            elif name == 'AOR':
                cls.mutation_operators[ast.UnaryOp].append(ArithmeticOperatorReplacement)
                cls.mutation_operators[ast.BinOp].append(ArithmeticOperatorReplacement)
            elif name == 'ASR':
                cls.mutation_operators[ast.AugAssign].append(AssignmentOperatorReplacement)
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

        if node.__class__ is not ast.UnaryOp: return node

        if node.op.__class__ is ast.USub or node.op.__class__ is ast.UAdd or node.op.__class__ is ast.Not:
            return node.operand

        return node


class ArithmeticOperatorReplacement(MutationOperator):

    @classmethod
    def name(cls):
        return 'AOR'

    @classmethod
    def mutate(cls, node):
        """
        mutate arithmetic addition, arithmetic subtraction
        """

        if node.__class__ is not ast.BinOp: return node

        # mutate arithmetic addition, arithmetic subtraction
        if node.op.__class__ is ast.Add:
            return ast.BinOp(left=node.left, op=ast.Sub(), right=node.right)
        if node.op.__class__ is ast.Sub:
            return ast.BinOp(left=node.left, op=ast.Add(), right=node.right)

        return node


class AssignmentOperatorReplacement(MutationOperator):

    @classmethod
    def name(cls):
        return "ASR"

    @classmethod
    def mutate(cls, node):
        """
        mutate +=, -=, *=, /=
        """

        if node.__class__ is not ast.AugAssign: return node

        # mutate +=, -=, *=, /=
        if node.op.__class__ is ast.Add:
            return ast.AugAssign(target=node.target, op=ast.Sub(), value=node.value)
        if node.op.__class__ is ast.Sub:
            return ast.AugAssign(target=node.target, op=ast.Add(), value=node.value)
        if node.op.__class__ is ast.Mult:
            return ast.AugAssign(target=node.target, op=ast.Div(), value=node.value)
        if node.op.__class__ is ast.Div:
            return ast.AugAssign(target=node.target, op=ast.Mult(), value=node.value)

        return node

