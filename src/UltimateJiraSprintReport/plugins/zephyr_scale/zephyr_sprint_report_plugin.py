# pylint: disable=import-outside-toplevel, protected-access
# pylint: disable=import-error, unused-import
# pylint: disable=too-few-public-methods, line-too-long
# pylint: disable=missing-function-docstring, invalid-name, missing-module-docstring, missing-class-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import numpy as np

from UltimateJiraSprintReport.plugins.plugin_register import Plugin
from UltimateJiraSprintReport.services._jira_service import JiraService
from UltimateJiraSprintReport.utils._pandas_utils import make_clickable
from UltimateJiraSprintReport.plugins.zephyr_scale.services.zephyr_scale_api_service import ZephyrScaleApiService
from UltimateJiraSprintReport.plugins.zephyr_scale.utils._pandas_utils import make_testcase_clickable

def flatten(xss):
    return [x for xs in xss for x in xs]

class ZephyrSprintReportPlugin(Plugin):

    def __init__(self, jira_service: JiraService, zephyr_api: str):
        super().__init__(jira_service)
        self.zephyr_service = ZephyrScaleApiService(zephyr_api)
        self.test_case_statistics_data_table = None

    def load_url(self, sprint_report_url: str):
        super()._set_sprint_details(sprint_report_url)

        self.test_case_statistics_data_table = self.process_issues()

        return self

    def process_issues(
            self,
            on_start: Callable[[float, str], None]=None,
            on_iteration: Callable[[str], None]=None,
            on_finish: Callable[[str], None]=None,
        ):

        if on_start is None:

            def on_start(_x, _y):
                pass

        if on_iteration is None:

            def on_iteration(_x):
                pass

        if on_finish is None:

            def on_finish(_x):
                pass

        issues = self.jira_service.get_sprint_issues(self.sprint_id)
        processed_issues = []

        def process_issue(issue):
            sprint_test_results = []
            issue_testcases = self.zephyr_service.get_test_cases(issue['key'])
            for tc in issue_testcases:
                testcase = self.zephyr_service.get_test_case(tc['self'])
                status = self.zephyr_service.get_test_case_status(testcase['status']['self'])
                executions = self.zephyr_service.get_test_case_latest_executions(testcase['key'])
                if executions['values']:
                    execution_status = self.zephyr_service.get_test_case_execution_status(executions['values'][0]['testExecutionStatus']['self'])
                else:
                    execution_status = {'name': 'Not Executed'}
                sprint_test_results.append({
                    "Issue Key": issue['key'],
                    "Issue Status": issue['fields']['status']['name'],
                    "Test Case": testcase['key'],
                    "Status": status['name'],
                    "Execution Status": execution_status['name']
                })
                on_iteration(f"issue={issue['key']}, testcase={testcase['key']}")
            return sprint_test_results

        on_start(len(issues), "Loading Zephyr Test Cases")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_issue, issue): issue for issue in issues}
            for future in as_completed(futures):
                result = future.result()
                processed_issues.append(result)
                on_iteration("done")

        on_iteration("Completed")

        processed_issues = flatten(processed_issues)
        df = pd.DataFrame(processed_issues)
        df["Issue Key"] = df["Issue Key"].apply(lambda x: make_clickable(x, self.base_url))
        df["Test Case"] = df["Test Case"].apply(lambda x: make_testcase_clickable(x, self.base_url, self.project))
        df = df.groupby(['Issue Key', 'Issue Status']).agg({
            'Test Case': lambda x: ', '.join(x) if len(x) > 0 else 'No Test Cases',
            'Status': lambda x: (x == 'Approved').sum() / len(x),
            'Execution Status': lambda x: (x == 'Pass').sum() / len(x)
        })
        df = df.sort_values(by=['Execution Status'], ascending=False).reset_index()
        df.loc['Total'] = df.mean(numeric_only=True, axis=0)
        df.loc['Total'] = df.loc['Total'].replace(np.nan, '', regex=True)

        df['Status'] = df['Status'].apply(lambda x: f"{x:.1%}")
        df['Execution Status'] = df['Execution Status'].apply(lambda x: f"{x:.1%}")

        on_finish("Done")

        return df

    def show_report(self):
        return "<h2>Sprint Test Case Statistics</h2>" + self.test_case_statistics_data_table.to_html(escape=False)
