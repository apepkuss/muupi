

class Calculator(object):
    @classmethod
    def add(cls, x, y):
        sum = x + y
        return sum

    @classmethod
    def floorDiv(cls, x, y):
        try:
            quotient = x // y
            return quotient
        except ZeroDivisionError:
            print "divided by zero"
        except:
            print "unknown exception"
        finally:
            print 0

if __name__ == "__main__":
    Calculator.floorDiv(5, 2)
    Calculator.add(5, 5)


