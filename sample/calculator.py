

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
        if y == 0:
            return None
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
        if y == 0:
            return None
        x //= y
        return x

    @classmethod
    def sum_all(cls, nums):
        n = len(nums)
        if not(n > 0):  # test COD
            return 0

        res = 0  # test CRP for numeric literals
        for i in xrange(n):   # test OIL (for)
            if nums[i] == 0:  # test COI
                continue
            res += nums[i]
        return res

    @classmethod
    def sum_all_while(cls, nums):   # test OIL (while)
        res = 0
        i = 0
        while i<len(nums):
            res += nums[i]
            i += 1
        return res

    @classmethod
    def get_version(cls):
        version = "1.2.3"
        return version

    @classmethod
    def divide_positiveInt(cls, x, y):
        if x>0 and y>0:
            quotient = x / y
            return quotient
        else:
            return None

    @classmethod
    def bit_negate(cls, x):
        return ~x

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


class CalculatorTest(object):

    @classmethod
    def test(cls):
        pass


def method_name():
    print 'this is a method'

if __name__ == "__main__":
    res = Calculator.floorDiv(5, 2)
    print res

