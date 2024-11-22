import dataclasses
import datetime
import importlib
import inspect
import logging
import os
from abc import abstractmethod
from concurrent.futures import ProcessPoolExecutor, wait
from dataclasses import dataclass
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Callable, Type

from storm_test.storm_reporters import StormReporter


class StormTestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"
    NOT_RUN = "NOT_RUN"
    IN_PROGRESS = "IN_PROGRESS"


class Scenario:
    def __init__(self, given, when, then):
        self.given = given
        self.when = when
        self.then = then


@dataclass
class StormTestStepObject:
    name: str
    method: Callable
    status: StormTestResult
    return_data = None
    error: str = None


@dataclass
class StormTestObject:
    name: str
    method: Callable
    status: StormTestResult
    error: str = None
    steps: list[StormTestStepObject] = None


@dataclass
class TestResult:
    passed: list = dataclasses.field(default_factory=list)
    failed: list = dataclasses.field(default_factory=list)
    skipped: list = dataclasses.field(default_factory=list)
    # not_run: list = dataclasses.field(default_factory=list)


@dataclass
class TestConfig:
    parameters: [any]
    configurations: [any]


def test_case(func, dep: Callable = None):
    func._dependency = dep
    func._test_case = True
    return func


def iter_test_case(func, dep: Callable = None, iter_object: list[dict] = None):
    func._dependency = dep
    func._iter_test_case = True
    func.test_funcs = []
    if iter_object:
        for test_object in iter_object:
            @test_case
            def iterated_test_case():
                iterated_test_case.__name__ = f"{func.__name__} - {object.__name__}"
                func(test_object)

            func.test_funcs.append(iterated_test_case)
    return func

    # test_funcs.append(iterated_test_case)


def set_up(func):
    func._test_setup = True
    return func


def teardown(func):
    func._test_teardown = True
    return func


def setup_each(func):
    func._setup_each = True
    return func


def teardown_each(func):
    func._teardown_each = True
    return func


class StormTest:
    _test_data = dict()
    _test_steps = []
    scenario: Scenario or [Scenario] or None = None
    preconditions = None
    postconditions = None
    test_id = None
    test_object: list[StormTestObject] = []
    test_status: StormTestResult = StormTestResult.NOT_RUN
    name = None

    @classmethod
    def set_up(cls):
        pass

    @classmethod
    def tear_down(cls):
        pass

    @classmethod
    def set_up_each(cls):
        pass

    @classmethod
    def tear_down_each(cls):
        pass

    @classmethod
    def run(cls, test_data=None):
        test_class = cls()
        test_class.name = cls.__name__
        logging.info(f"Running test item: {cls.__name__}")
        test_class.test_status = StormTestResult.IN_PROGRESS
        for name, method in inspect.getmembers(test_class, inspect.ismethod):
            name_string = name.replace("_", " ")
            if hasattr(method, "_test_case"):
                test_object = StormTestObject(
                    name=name_string,
                    method=method,
                    status=StormTestResult.NOT_RUN,
                )
                test_class.test_object.append(test_object)
            if hasattr(method, "_iter_test_case"):
                iter_tests = getattr(method, "test_funcs", method)
                for test in iter_tests:
                    test_object = StormTestObject(
                        name=test.__name__.replace("_", " "),
                        method=test,
                        status=StormTestResult.NOT_RUN,
                    )
                    test_class.test_object.append(test_object)
        try:
            test_class.set_up()
        except Exception as e:
            logging.error("Test setup failed.  Reason: %s", e)
            test_class.test_status = StormTestResult.FAIL
        for test_object in cls.test_object:
            try:
                logging.info(f"Running test item: {getattr(test_object, 'name')}")
                test_object.status = StormTestResult.IN_PROGRESS
                test_class.set_up_each()
                test_data and test_object.method(test_class, test_data) or test_object.method(test_class)
                test_class.tear_down_each()
                test_object.status = StormTestResult.PASS
            except Exception as e:
                test_object.status = StormTestResult.FAIL
                test_object.error = str(e)

            if test_class._test_steps:
                test_object.steps = cls._test_steps
                test_class._test_steps = None
            test_class.test_status = StormTestResult.PASS
        try:
            test_class.tear_down()
        except Exception as e:
            logging.error("Test teardown failed.  Reason: %s", e)
            test_class.test_status = StormTestResult.FAIL
        return test_class

        # try:
        #     self.set_up()
        #     if isinstance(cls._test, list):
        #         for storm_test in cls._test:
        #             storm_test(*args, **kwargs)
        #             cls._test_result.append({storm_test.__name__.replace('_', ' '): StormTestResult.PASS})
        #     else:
        #         cls._test(*args, **kwargs)
        #     cls.tear_down()
        #     cls._test_result.append({cls._test_name: StormTestResult.PASS})
        # except Exception as e:
        #     cls._test_result.append({cls._test_name: {StormTestResult.FAIL: str(e)}})

    @classmethod
    def validate(cls, name: str, test: bool, fail_msg=None):
        """
        Used to assert if an object is true.
        If so, adds storm_test and passes.
        If not, adds to failures with fail message.
        """
        if test:
            cls._test_steps.append({name: StormTestResult.PASS})
        else:
            cls._test_steps.append({name: {StormTestResult.FAIL: fail_msg}})


class StormTestSuite:
    def __init__(
            self,
            name: str,
            tests: list[StormTest] = None,
            # test_dir: PathLike = os.path.join(os.getcwd(), "tests"),
            test_data: dict = None,
    ):
        self.tests = tests or []
        self.name = name
        self.test_results = []
        # self.test_dir = test_dir
        self.test_data = test_data

        # if self.test_dir:
        #     if self.tests is None:
        #         self.tests = []
        #     for file in Path(self.test_dir).glob("*_test.py"):
        #         module_name = file.stem
        #
        #         module = importlib.import_module(module_name)
        #
        #         for name, cls in inspect.getmembers(module, inspect.isclass):
        #             if getattr(cls, "StormTestCase", False):
        #                 self.tests.append(cls)
        #
        #         for item in module.__all__:
        #             if isinstance(item, StormTest):
        #                 self.tests.append(item)

    def map_results(self, results):
        """
        Function that automatically runs upon initialization, or if test results is None.  Also maps test retries, but
        does not process them, so one will need to run the "process retries" as a followup, AFTER executing the retry
        logic, which is not included in this class.

        :return:
        """
        for result in results:
            result = result.result()
            self.test_results += result

            # self.test_results.passed = [
            #     test_object
            #     for test_object in self
            #     if t.result().test_status == StormTestResult.PASS
            # ]
            #
            # self.test_results.failed = [
            #     getattr(t.result(), "name")
            #     for t in results
            #     if t.result().test_status == StormTestResult.FAIL
            # ]
            #
            # self.test_results.skipped = [
            #     getattr(t.result(), "name")
            #     for t in results
            #     if t.result().test_status == StormTestResult.SKIPPED
            # ]


class StormTestRunner:
    def __init__(
            self,
            test_cases: list[StormTest] = None,
            test_suites: list[StormTestSuite] = None,
            test_data: dict = None,
            reporting: StormReporter = None,
    ):
        #Setup logging

        time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_path = Path.cwd() / "logs" / f"storm_test_{time_stamp}.log"
        logging.basicConfig(level=logging.INFO, filename=log_path, filemode="w+")


        self.test_suites = test_suites or []
        if test_cases:
            self.test_suites.append(
                StormTestSuite(
                    name="Generic_Test_Suite",
                    tests=test_cases,
                    test_data=test_data))
        self.test_results = []

    def run_tests(self, test_data=None):
        logging.info("Starting test run")
        if self.test_suites:
            for test_suite in self.test_suites:
                logging.info(f"Running test suite {test_suite.name}")
                test_data = test_data or test_suite.test_data
                results = multiprocess_runner(test_suite.tests, test_data)
                for result in results:
                    result = result.result()
                    test_suite.test_results.append(result)
                print(f"Test result {test_suite.name}:")
                for test_result in test_suite.test_results:
                    print(f"{test_result.name}: {test_result.test_status.value}")
                    print("Steps:")
                    for test_object in test_result.test_object:
                        print(f"{test_object.name}: {test_object.status.value}")

        else:
            logging.warning("No test suites defined")
        logging.info("Finished test run")

        # print(
        #     f"Test results: "
        #     f"Passed:{self.test_results.passed} "
        #     f"Failed:{self.test_results.failed} "
        #     f"Skipped:{self.test_results.skipped}"
        # )
        # logging.info(
        #     f"Test results: "
        #     f"Passed:{self.test_results.passed} "
        #     f"Failed:{self.test_results.failed} "
        #     f"Skipped:{self.test_results.skipped}"
        # )
        # TODO: write out test runner portion

        # self.test_results.not_run = [
        #     t.result().name
        #     for t in self.result_futures
        #     if t.result().result == ArvestTestResult.NotRun
        # ]
        # self.test_to_retry = [
        #     t.result()
        #     for t in self.result_futures
        #     if (
        #                t.result().result == ArvestTestResult.Fail
        #                or t.result().result == ArvestTestResult.Error
        #        )
        #        and t.result().retry is True
        # ]


def multiprocess_runner(
        tests: list[StormTest],
        test_data: dict = None,
        max_workers: int = 1,
        initializer=None,
        init_args=None,

):
    futures_result = []

    if not tests or len(tests) == 0:
        print("No tests specified for mutliprocess runner, exiting.")
        return futures_result

    with ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=initializer,
            initargs=init_args
    ) as executor:
        for test in tests:
            test_result_future = executor.submit(test.run, test_data)
            futures_result.append(test_result_future)

    wait(futures_result)

    return futures_result
