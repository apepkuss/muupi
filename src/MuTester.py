

class MuTester(object):

    def __init__(self):
        self.suite = None
        self.sut = None

    def run(self, suite, sut):
        """
        Runs all test cases in a specified test suite on an sut.
        Returns the raw test result.
        """
        self.suite = suite
        self.sut = sut
        pass