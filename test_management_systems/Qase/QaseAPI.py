import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
import dotenv
import requests

from test_management_connector.Qase.qase_submit_bulk import submit_bulk_test_results

dotenv.load_dotenv()

QASE_API_KEY = os.getenv('QASE_API_KEY')
QASE_TEST_RUN_ENDPOINT = 'https://api.qase.io/v1/run/'
QASE_BASE_URL = 'https://api.qase.io/v1'


class QaseStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class QaseTestStep:
    action: str
    expected_result: str
    data: str
    attachments: [str]


# 'URL': f'https://api.qase.io/v1/result/{project_code}/{run_id}/bulk',

@dataclass
class QaseTestCase:
    description: str
    preconditions: str
    postconditions: str
    title: str
    severity: int
    priority: int
    behavior: int
    type: int
    layer: int
    is_flaky: int
    author_id: int
    suite_id: int
    suite_name: str
    milestone_id: int
    automation: int
    status: int
    attachments: [str]
    steps: [QaseTestStep]
    tags: [str]
    params: dict

    def create_result(
            self,
            case_id: int = None,
            test_duration: int = None,
            error_message: str | Exception = None,
            comment: str = None,
    ):
        steps = []
        if self.steps:
            for step in self.steps:
                steps.append(step.__dict__)
        else:
            steps = None

        if case_id:
            return {
                "case_id": case_id,
                "status": self.status,
                "time": test_duration,
                "defect": False,
                "attachments": self.attachments,
                "stacktrace": str(error_message),
                "comment": comment,
                "param": self.params,
                "steps": steps,
                "author_id": self.author_id,
            }

        return {
            "case": {
                "title": self.title,
                "suite_title": self.suite_name,
                "description": self.description,
                "preconditions": self.preconditions,
                "postconditions": self.postconditions,
            },
            "status": self.status,
            "time": test_duration,
            "defect": False,
            "attachments": self.attachments,
            "stacktrace": str(error_message),
            "comment": comment,
            "param": self.params,
            "steps": steps,
            "author_id": self.author_id,
        }

    def create_case_body(self):
        body_dict = self.__dict__
        body_dict.pop("create_result")
        body_dict.pop("create_result")
        return body_dict


class QaseTestRun:
    def __init__(
            self,
            test_run_name: str,
            test_run_description: str = "Automated Test Run",
            project_code: str = "TRAIN2",
            test_case_ids: [int] = None,
    ):
        self.test_run_name = test_run_name
        self.test_run_description = test_run_description
        self.project_code = project_code
        self.test_case_ids = test_case_ids
        self.url = QASE_TEST_RUN_ENDPOINT + self.project_code
        self.run_id = None

    def start_run(self):
        default_header = {
            "Token": QASE_API_KEY,
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        try:
            payload = {
                "title": self.test_run_name,
                "description": self.test_run_description,
                "is_autotest": True
            }
            response = requests.post(
                self.url,
                headers=default_header,
                json=payload,
                timeout=15,
            )
            response = json.loads(response.text)
            self.run_id = response["result"]["id"]

        except Exception as e:
            logging.error(e)


    def _complete_run(self):
        """
       Runs api call to change the storm_test run's status to Complete. Not to be used outside of class.
       :return:
       """

        url = f"{QASE_TEST_RUN_ENDPOINT}{self.project_code}/{self.run_id}/complete"
        default_header = {
            "Token": QASE_API_KEY,
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=default_header)
        if response.ok:
            return
        else:
            logging.error(f"Unable to complete storm_test run for ID: {self.run_id}")

    def submit_run_results(self, results: list):
        submit_bulk_test_results(self.project_code, self.run_id, QASE_API_KEY, results)
        self._complete_run()
