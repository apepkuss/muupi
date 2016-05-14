from abc import *


class MutationOperator(object):
    __metaclass__ = ABCMeta

    @classmethod
    def type(cls):
        return cls.__class__


class ArithmeticOperator(MutationOperator):
    __metaclass__ = ABCMeta


class ArithmeticOperatorDeletion(ArithmeticOperator):

    @classmethod
    def name(cls):
        return 'AOD'


class ArithmeticOperatorReplacement(ArithmeticOperator):

    @classmethod
    def name(cls):
        return 'AOR'
