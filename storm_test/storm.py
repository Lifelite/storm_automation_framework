import dataclasses
import importlib
import inspect
import logging
import os
from abc import abstractmethod
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
class TestConfig:
    parameters: [any]
    configurations: [any]

def test_case(func, dep: Callable = None):
    func._dependency = dep
    func._test_case = True
    return func


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

    @classmethod
    @abstractmethod
    def set_up(cls):
        pass

    @classmethod
    @abstractmethod
    def tear_down(cls):
        pass

    @classmethod
    @abstractmethod
    def set_up_each(cls):
        pass

    @classmethod
    @abstractmethod
    def tear_down_each(cls):
        pass

    @classmethod
    def run(cls, test_data=None):
        test_class = cls()
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
        try:
            test_class.set_up()
        except Exception as e:
            logging.error("Test setup failed.  Reason: %s", e)
            test_class.test_status = StormTestResult.FAIL
        for test_object in cls.test_object:
            try:
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
            tests: list[StormTest] = None,
            test_dir: PathLike = os.path.join(os.getcwd(), "tests"),
            test_data: dict = None,
    ):
        self.tests = tests or []
        self.test_dir = test_dir
        self.test_data = test_data

        if self.test_dir:
            if self.tests is None:
                self.tests = []
            for file in Path(self.test_dir).glob("*_test.py"):
                module_name = file.stem

                module = importlib.import_module(module_name)

                for name, cls in inspect.getmembers(module, inspect.isclass):
                    if getattr(cls, "StormTestCase", False):
                        self.tests.append(cls)

                for item in module.__all__:
                    if isinstance(item, StormTest):
                        self.tests.append(item)


@dataclass
class TestResult:
    passed: list = dataclasses.field(default_factory=list)
    failed: list = dataclasses.field(default_factory=list)
    errored: list = dataclasses.field(default_factory=list)
    not_run: list = dataclasses.field(default_factory=list)





class StormTestRunner:
    def __init__(
            self,
            test_cases: list[StormTest] = None,
            test_suites: StormTestSuite or list[Type[StormTestSuite]] = None,
            reporting: StormReporter = None,
    ):
        if test_cases:
            self.test_cases = StormTestSuite(test_cases)
        self.test_suites = test_suites

# class StormTestRunner:
#     def __init__(self, tests)
