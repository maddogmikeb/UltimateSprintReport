# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments
# pylint: disable=unnecessary-lambda, protected-access, consider-using-f-string, wrong-import-order

import json
import requests

ZEPHYR_API_URL = "https://api.zephyrscale.smartbear.com/v2"


class ZephyrScaleApiService():

    def __init__(self, zephyr_api: str, cache_results: bool=True):
        self.cache_results = cache_results
        self.cache = {}

        if zephyr_api is None:
            raise ValueError("Zephyr Scale API Key not set")
        self.zephyr_api = zephyr_api
        self.headers = {"Authorization": f"Bearer {self.zephyr_api}"}

    def clear_cache(self):
        self.cache = {}

    def get_test_cases(self, issue_key: str):
        return json.loads(
            requests.get(
                f"{ZEPHYR_API_URL}/issuelinks/{issue_key}/testcases",
                headers=self.headers,
                timeout=5
            ).text
        )

    def get_test_case(self, test_case_url: str):
        if not test_case_url.startswith(ZEPHYR_API_URL):
            raise ValueError("Invalid host or differs from Zephyr")

        return json.loads(
            requests.get(
                test_case_url,
                headers=self.headers,
                timeout=5
            ).text
        )

    def get_test_case_status(self, test_case_status_url: str):
        if not test_case_status_url.startswith(ZEPHYR_API_URL):
            raise ValueError("Invalid host or differs from Zephyr")

        return json.loads(
            requests.get(
                test_case_status_url,
                headers=self.headers,
                timeout=5
            ).text
        )

    def get_test_case_latest_executions(self, test_case_key: str):
        return json.loads(
            requests.get(
                f"{ZEPHYR_API_URL}/testexecutions?testCase={test_case_key}&onlyLastExecutions=true",
                headers=self.headers,
                timeout=5
            ).text
        )

    def get_test_case_execution_status(self, test_case_execution_status_url: str):
        return json.loads(
            requests.get(
                test_case_execution_status_url,
                headers=self.headers,
                timeout=5
            ).text
        )
