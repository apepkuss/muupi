

class MuAnalyzer(object):

    @classmethod
    def analyze(cls, results):
        """
        Analyzes a test result, computes mutation scores, and makes a final test report.
        """
        if len(results) == 0:
            return
        # number of killed mutants
        mutant_killed = 0
        # total number of mutants
        mutant_total = len(results)

        for result in results:
            if len(result.failures) > 0 or len(result.errors) > 0:
                mutant_killed += 1

        mutation_score = mutant_killed * 1.0 / mutant_total
        print "\n\nmutation score: " + str(mutation_score)

