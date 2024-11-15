from storm_test.storm import StormTestSuite, StormTestRunner
from tests.bdd_test import BDDTest
from tests.test import TestTheThing

# full_test_suit = StormTestSuite(
#     tests = [
#         TestTheThing(),
#         TestTheThing()
#     ]
# )



test_suite = StormTestSuite("Testing")

test_suite.tests = [
    TestTheThing,
]






if __name__ == '__main__':
    TestTheThing.run()
    StormTestRunner(test_suites=[test_suite]).run_tests()
    # BDDTest.run_scenario()






