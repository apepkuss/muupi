

class MuAnalyzer(object):

    @classmethod
    def analyze(cls, results):
        """
        Analyzes a test result, computes mutation scores, and makes a final test report.
        """
        # number of killed mutants
        mutant_killed = 0
        # total number of mutants
        mutant_total = len(results)
        failures = []

        for result in results:
            if result.failures is not None and len(result.failures) > 0:
                failures += [failure[0] for failure in result.failures]
                mutant_killed += 1

        mutation_score = mutant_killed * 1.0 / mutant_total
        print "\n\nmutation score: " + str(mutation_score)

