import logging
import unittest
from dataclasses import dataclass
from typing import List
from StormTestLoader import StormTestLoader

@dataclass
class TestParams:
    test_suites: List[str]
    test_data: dict
    retry: bool

@dataclass
class TestRunInstance:
    run_name: str
    run_id: int
    test_params: TestParams
    success: bool = False


def handle_test_request(run_name, run_id, test_params: dict):

    configured_params = TestParams(
        test_suites=test_params.get('test_suites'),
        test_data=test_params.get('test_data'),
        retry=bool(test_params.get('retry')),
    )

    if configured_params.test_suites is None or not isinstance(configured_params.test_suites, list | str):
        logging.error("No Test Suites specified")
        return

    test_run = TestRunInstance(
        run_name=run_name,
        run_id=run_id,
        test_params=configured_params
    )

    suite = StormTestLoader().load_tests_from_suite(suite=configured_params.test_suites)
    unittest.TextTestRunner(verbosity=2).run(suite)



