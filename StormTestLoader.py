import logging
import os
import unittest


class StormTestLoader:
    tests = unittest.TestSuite()
    loader = unittest.TestLoader()

    def load_tests_from_suite(self, suite=None):
        discover = lambda test_dir: self.loader.discover(test_dir, pattern='*.py')

        for root, dirs, files in os.walk("test_suites"):
            discovered_tests = None
            if isinstance(suite, list):
                    if os.path.basename(root) in suite:
                        discovered_tests = discover(root)
            elif isinstance(suite, str):
                    if os.path.basename(root) == suite:
                        discovered_tests = discover(root)
            else:
                discovered_tests = discover(root)
            if discovered_tests:
                self.tests.addTests(discovered_tests)
        return self.tests







