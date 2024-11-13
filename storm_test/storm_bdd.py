import dataclasses
import importlib
import inspect
import os
from dataclasses import dataclass
from enum import Enum
from itertools import product
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
class TestData:
    parameters: [any]
    configurations: [any]


class GerkinStep(Enum):
    GIVEN = "GIVEN"
    WHEN = "WHEN"
    THEN = "THEN"

def skip_if(func, condition: [callable] or callable):
    func._skip_condition = condition
    return func


def given(func):
    func._gerkin = GerkinStep.GIVEN
    func.name = f"GIVEN {func.__name__.replace("_", " ")}"

    return func


def when(func):
    func._gerkin = GerkinStep.WHEN
    func.name = f"WHEN {func.__name__.replace("_", " ")}"
    return func


def then(func):
    func._gerkin = GerkinStep.THEN
    func.name = f"THEN {func.__name__.replace("_", " ")}"
    return func


def can_fail(func: when):
    func._can_fail = True
    return func


def test_step(func, gerkin_step: GerkinStep):
    name_string = func.__name__.replace("_", " ")
    func._gerkin = gerkin_step
    match gerkin_step:
        case GerkinStep.GIVEN:
            func._behavior = f"GIVEN {name_string}"
        case GerkinStep.WHEN:
            func._behavior = f"WHEN {name_string}"
        case GerkinStep.THEN:
            func._behavior = f"THEN {name_string}"
        case _:
            pass
    return func


@dataclass
class StormBehaviorResult:
    scenario: Scenario
    result: StormTestResult = StormTestResult.IN_PROGRESS


class StormBehaviorDrivenTest:
    _test_data = dict()
    _test_steps = {
        GerkinStep.GIVEN: [],
        GerkinStep.WHEN: [],
        GerkinStep.THEN: [],
    }
    scenarios: Scenario or [Scenario] or None = []
    preconditions = None
    postconditions = None
    test_id = None
    test_object: list[StormTestObject] = []
    test_status: StormTestResult = StormTestResult.NOT_RUN


    @staticmethod
    def _check_condition(method_a, method_b):
        condition_a = getattr(method_a, "_skip_condition", False)
        condition_b = getattr(method_b, "_skip_condition", False)
        if condition_a == method_b:
            return True
        elif condition_b == method_a:
            return True
        else:
            return False




    @classmethod
    def run_decision_matrix(cls, test_data=None):
        current_data_state = test_data
        test_class = cls()
        test_class.test_status = StormTestResult.IN_PROGRESS
        for step_name, step_method in inspect.getmembers(test_class, inspect.ismethod):
            if hasattr(step_method, "_gerkin"):
                gerkin_step = getattr(step_method, "_gerkin")
                test_class._test_steps[gerkin_step].append(
                    StormTestStepObject(
                        name=getattr(step_method, 'name', step_method.__name__),
                        method=step_method,
                        status=StormTestResult.NOT_RUN,
                    )
                )

        for scenario_given, scenario_when in product(
                test_class._test_steps[GerkinStep.GIVEN],
                test_class._test_steps[GerkinStep.WHEN],
        ):
            if cls._check_condition(scenario_given, scenario_when):
                continue
            scenario_given.status = StormTestResult.IN_PROGRESS
            scenario_when.status = StormTestResult.IN_PROGRESS
            try:
                current_data_state = scenario_given.method(current_data_state)
                scenario_given.status = StormTestResult.PASS
            except Exception as e:
                scenario_given.status = StormTestResult.FAIL
                scenario_given.error = str(e)
            try:
                current_data_state = scenario_when.method(current_data_state)
                scenario_when.status = StormTestResult.PASS
            except Exception as e:
                scenario_when.status = StormTestResult.FAIL
                scenario_when.error = str(e)

            then_senarios = []

            for scenario_then in test_class._test_steps[GerkinStep.THEN]:
                if (
                    cls._check_condition(scenario_then, scenario_when)
                    or
                    cls._check_condition(scenario_then, scenario_given)
                    ):
                    continue
                scenario_then.status = StormTestResult.IN_PROGRESS
                try:
                    then_result = scenario_then.method(current_data_state)
                    if isinstance(then_result, bool) and then_result or then_result is None:
                        scenario_then.status = StormTestResult.PASS
                    elif getattr(scenario_then.method, "_can_fail", False):
                        scenario_then.status = StormTestResult.SKIPPED
                    else:
                        scenario_then.status = StormTestResult.FAIL
                except Exception as e:
                    scenario_then.status = StormTestResult.FAIL
                    scenario_then.error = str(e)
                then_senarios.append(scenario_then)

            then_string = then_senarios[0].name
            then_full_status = StormTestResult.PASS
            for scenario in then_senarios:
                if scenario.status == StormTestResult.FAIL:
                    then_full_status = StormTestResult.FAIL
                if scenario.name == then_string:
                    continue
                current_scenario =  scenario.name.replace("THEN", "\nAND")
                then_string += current_scenario


            test_class.scenarios.append(
                StormBehaviorResult(
                    scenario=Scenario(scenario_given.name, scenario_when.name, then_string),
                    result=StormTestResult.PASS if (
                            scenario_given.status == StormTestResult.PASS
                            and scenario_when.status == StormTestResult.PASS
                            and then_full_status == StormTestResult.PASS
                    ) else StormTestResult.FAIL,
                ))
        return test_class.scenarios

    # @classmethod
    # def get_scenario_results(cls, scenario_list:StormBehaviorResult):
    #

    @classmethod
    def validate(cls, name: str, test: bool, fail_msg=None):
        """
        Used to assert if an object is true.
        If so, adds storm_test and passes.
        If not, adds to failures with fail message.
        """
        return test if test else f"{test} FAILED, REASON: {fail_msg}"


class StormBehaviorDrivenTestSuite:
    def __init__(
            self,
            tests: list[StormBehaviorDrivenTest] = None,
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
                    if isinstance(item, StormBehaviorDrivenTest):
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
            test_cases: list[StormBehaviorDrivenTest] = None,
            test_suites: StormBehaviorDrivenTestSuite or list[Type[StormBehaviorDrivenTestSuite]] = None,
            reporting: StormReporter = None,
    ):
        if test_cases:
            self.test_cases = StormBehaviorDrivenTestSuite(test_cases)
        self.test_suites = test_suites

# class StormTestRunner:
#     def __init__(self, tests)
