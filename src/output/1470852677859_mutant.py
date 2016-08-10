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
        if (y == 0):
            return None
        quotient = x / y
        return quotient

    @classmethod
    def negate(cls, x):
        return (+x)

    @classmethod
    def floorDiv(cls, x, y):
        try:
            quotient = x // y
            return quotient
        except ZeroDivisionError:
            print 'divided by zero'
        except:
            print 'unknown exception'

    @classmethod
    def floorDivAssign(cls, x, y):
        if (y == 0):
            return None
        x //= y
        return x

    @classmethod
    def sum_all(cls, nums):
        n = len(nums)
        if (not (n > 0)):
            return 0
        res = 0
        for i in xrange(n):
            flag = (nums[i] == 0)
            if flag:
                continue
            res += nums[i]
        return res

    @classmethod
    def sum_all_while(cls, nums):
        res = 0
        i = 0
        while (i < len(nums)):
            res += nums[i]
            i += 1
        return res

    @classmethod
    def get_version(cls):
        version = '1.2.3'
        return version

    @classmethod
    def divide_positiveInt(cls, x, y):
        if ((x > 0) and (y > 0)):
            quotient = x / y
            return quotient
        else:
            return None

    @classmethod
    def bit_negate(cls, x):
        return (~x)

    @classmethod
    def bit_and(cls, x, y):
        return x & y

    @classmethod
    def bit_or(cls, x, y):
        return x | y

    @classmethod
    def bit_xor(cls, x, y):
        return x ^ y

    @classmethod
    def bit_left_shift(cls, x):
        return x << 1

    @classmethod
    def bit_right_shift(cls, x):
        return x >> 1

    @classmethod
    def sum_of_collection(cls, nums, start, end, step):
        res = 0
        if (len(nums) > 0):
            for anum in nums[start:end:step]:
                res += anum
        return res


class ScientificCalculator(Calculator):

    @classmethod
    def add(cls, x, y):
        '\n        Override add function defined in Calculator\n        :param x:\n        :param y:\n        :return:\n        '
        pass

    @classmethod
    def subtract(cls, x, y):
        '\n        Override subtract function defined in Calculator\n        :param x:\n        :param y:\n        :return:\n        '
        pass

    @classmethod
    def multiply(cls, x, y):
        '\n        Override multiply function defined in Calculator\n        :param x:\n        :param y:\n        :return:\n        '
        pass

    @classmethod
    def divide(cls, x, y):
        '\n        Override divide function defined in Calculator\n        :param x:\n        :param y:\n        :return:\n        '
        pass


class CalculatorTest(object):

    def __init__(self):
        self.name = 'name_value'
        text = self.name

    def get_name(self):
        return self.name

def method_name():
    print 'this is a method'
if (__name__ == '__main__'):
    res = Calculator.floorDiv(5, 2)
    print res