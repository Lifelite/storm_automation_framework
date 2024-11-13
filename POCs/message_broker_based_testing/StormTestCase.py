import enum
import logging
import unittest
from dataclasses import dataclass


class TestStepResult(enum.Enum):
    PASS = "passed"
    FAIL = "failed"
    SKIP = "skipped"
    PENDING = "pending"

@dataclass
class TestStep:
    name: str
    result: TestStepResult = TestStepResult.PENDING
    artifact: [str | object] = None
    stacktrace: Exception = None

class StormTestCase(unittest.TestCase):

    description = ''
    preconditions = ''
    postconditions = ''
    story_link = ''
    test_steps = []
    current_step: TestStep | None = None

    def start_test_step(self, name):
        if self.current_step and self.current_step.result == TestStepResult.PENDING:
            self.current_step.result = TestStepResult.PASS
            for test_step in self.test_steps:
                if test_step.name == name:
                    self.test_steps[self.test_steps.index(test_step)] = test_step
                    logging.WARN("Be sure to use self.end_test_step to properly finish previous step!")
        self.current_step = TestStep(name=name, result=TestStepResult.PENDING)

    def end_test_step(self, artifact: any = None, stacktrace: Exception = None):
        if not self.current_step:
            logging.WARN("No storm_test step to finish!")
            return
        if stacktrace:
            self.current_step.stacktrace = stacktrace
            self.current_step.result = TestStepResult.FAIL
        self.current_step.artifact = artifact
        self.test_steps.append(self.current_step)
        self.current_step = None
