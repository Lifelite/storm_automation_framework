from storm_test.storm import StormTestSuite
from tests.bdd_test import BDDTest
from tests.test import TestTheThing

# full_test_suit = StormTestSuite(
#     tests = [
#         TestTheThing(),
#         TestTheThing()
#     ]
# )






if __name__ == '__main__':
    #TestTheThing.run()
    BDDTest.run_decision_matrix()






