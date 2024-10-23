import unittest


from StormTestLoader import StormTestLoader

suite = StormTestLoader().load_tests_from_suite(["sample_tests"])
unittest.TextTestRunner(verbosity=2).run(suite)
