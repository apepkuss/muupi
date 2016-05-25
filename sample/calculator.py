

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
        quotient = x / y  # y=0 is a bug
        return quotient

    @classmethod
    def negate(cls, x):
        return -x

    @classmethod
    def floorDiv(cls, x, y):
        quotient = x // y
        return quotient

    @classmethod
    def floorDivAssign(cls, x, y):
        x //= y
        return x

    @classmethod
    def sum_all(cls, nums):
        n = len(nums)
        if not(n == 0):
            return 0

        res = 0
        for i in xrange(n):
            if nums[i] == 0:
                continue
            res += nums[i]
        return res


class CalculatorTest(object):

    @classmethod
    def test(cls):
        pass


def method_name():
    print 'this is a method'

if __name__ == "__main__":
    res = Calculator.floorDiv(5, 2)
    print res

