PASS = "PASS"
FAIL = "FAIL"
SKIPPED = "SKIPPED"

class ThreeValuedLogic:
    def and_all(self, results):
        final = PASS
        for r in results:
            if r == FAIL:
                return FAIL
            if r == SKIPPED:
                final = SKIPPED
        return final