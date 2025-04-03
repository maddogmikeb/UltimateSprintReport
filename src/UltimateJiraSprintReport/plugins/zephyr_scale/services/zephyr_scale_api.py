# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments
# pylint: disable=unnecessary-lambda, protected-access, consider-using-f-string, wrong-import-order

import json
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import numpy as np
from tqdm.auto import tqdm


ZEPHYR_API_URL = "https://api.zephyrscale.smartbear.com/v2"


def load_sprint_zephyr_test_cast_statistics(self, zephyr_api):
    if zephyr_api is None:
        raise ValueError("Zephyr Scale API Key not set")
    if self.sprintId is None:
        raise ValueError("Sprint ID not set")
    if self.base_url is None:
        raise ValueError("Base URL not set")

    def flatten(xss):
        return [x for xs in xss for x in xs]

    headers = {"Authorization": f"Bearer {zephyr_api}"}
    issues = json.loads(self.jira.request(absolute=True, method="GET", path=f"{self.base_url}/rest/agile/1.0/sprint/{self.sprintId}/issue").text)['issues']
    status_cache = {}
    executions_cache = {}
    processed_issues = []

    def process_issue(issue, progress_bar):
        sprint_test_results = []
        issue_testcases = json.loads(requests.get(f"{ZEPHYR_API_URL}/issuelinks/{issue['key']}/testcases", headers=headers, timeout=5).text)
        for tc in issue_testcases:
            testcase = json.loads(requests.get(tc['self'], headers=headers, timeout=5).text)
            status = status_cache.get(testcase['status']['self']) or json.loads(requests.get(testcase['status']['self'], headers=headers, timeout=5).text)
            status_cache[testcase['status']['self']] = status
            executions = json.loads(requests.get(f"{ZEPHYR_API_URL}/testexecutions?testCase={testcase['key']}&onlyLastExecutions=true", headers=headers, timeout=5).text)
            if executions['values']:
                execution_status = executions_cache.get(executions['values'][0]['testExecutionStatus']['self']) or json.loads(requests.get(executions['values'][0]['testExecutionStatus']['self'], headers=headers, timeout=5).text)
                executions_cache[executions['values'][0]['testExecutionStatus']['self']] = execution_status
            else:
                execution_status = {'name': 'Not Executed'}
            sprint_test_results.append({
                "Issue Key": issue['key'],
                "Issue Status": issue['fields']['status']['name'],
                "Test Case": testcase['key'],
                "Status": status['name'],
                "Execution Status": execution_status['name']
            })
            progress_bar.set_postfix(issue=issue['key'], testcase=testcase['key'])
        return sprint_test_results

    with tqdm(total=len(issues), desc="Loading Zephyr Test Cases", unit="issue") as progress_bar:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_issue, issue, progress_bar): issue for issue in issues}
            for future in as_completed(futures):
                result = future.result()
                processed_issues.append(result)
                progress_bar.update(1)
        progress_bar.refresh()
        progress_bar.set_postfix_str("Completed")

    processed_issues = flatten(processed_issues)
    df = pd.DataFrame(processed_issues)
    df["Issue Key"] = df["Issue Key"].apply(lambda x: self._make_clickable(x))
    df["Test Case"] = df["Test Case"].apply(lambda x: self._make_testcase_clickable(x))
    df = df.groupby(['Issue Key', 'Issue Status']).agg({
        'Test Case': lambda x: ', '.join(x),
        'Status': lambda x: (x == 'Approved').sum() / len(x),
        'Execution Status': lambda x: (x == 'Pass').sum() / len(x)
    })
    df = df.sort_values(by=['Execution Status'], ascending=False).reset_index()
    df.loc['Total'] = df.mean(numeric_only=True, axis=0)
    df.loc['Total'] = df.loc['Total'].replace(np.nan, '', regex=True)

    df['Status'] = df['Status'].map('{:.1%}'.format)
    df['Execution Status'] = df['Execution Status'].map('{:.1%}'.format)

    self.progress_bar.n = 100
    self.progress_bar.refresh()
    self.progress_bar.close()

    self.test_case_statistics_data_table = df

    return self
