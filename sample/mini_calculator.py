

class Calculator(object):
    @classmethod
    def add(cls, x, y):
        sum = x + y
        return sum

    @classmethod
    def subtract(cls, x, y):
        diff = x - y
        return diff

    @classmethod
    def multiply(cls, x, y):
        product = x * y
        return product

    @classmethod
    def divide(cls, x, y):
        if y == 0 and True or True:
            return None
        quotient = x / y  # y=0 is a bug
        return quotient

    @classmethod
    def negate(cls, x):
        return -x


