# pylint: disable=import-outside-toplevel, protected-access
# pylint: disable=import-error, unused-import, wrong-import-order
# pylint: disable=too-few-public-methods, line-too-long
# pylint: disable=missing-function-docstring, invalid-name, missing-module-docstring, missing-class-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm.auto import tqdm

from UltimateJiraSprintReport.plugins.plugin_register import Plugin
from UltimateJiraSprintReport.plugins.zephyr_scale.services.zephyr_scale_api_service import ZephyrScaleApiService
from UltimateJiraSprintReport.plugins.zephyr_scale.utils._pandas_utils import make_testcase_clickable
from UltimateJiraSprintReport.services._jira_service import JiraService
from UltimateJiraSprintReport.utils._pandas_utils import make_clickable
import numpy as np
import pandas as pd


def flatten(xss):
    return [x for xs in xss for x in xs]


class ZephyrSprintReportPlugin(Plugin):

    def __init__(self, jira_service: JiraService, zephyr_api: str):
        super().__init__(jira_service)
        self.zephyr_service = ZephyrScaleApiService(zephyr_api)
        self.test_case_statistics_data_table = None

        self.progress_bar = None

    def load(self):

        self.progress_bar = tqdm(total=100, desc="Loading Test Case Details", leave=True)
        self.progress_bar.n = 0
        self.progress_bar.refresh()

        def on_start(total, text):
            if not total is None:
                if self.progress_bar.total > 0:
                    self.progress_bar.total = self.progress_bar.total + total
                else:
                    self.progress_bar.total = total
            self.progress_bar.set_postfix_str(text)
            self.progress_bar.refresh()

        def on_iteration(text):
            self.progress_bar.update(1)
            self.progress_bar.set_postfix_str(text)
            self.progress_bar.refresh()

        def on_finish(text):
            self.progress_bar.set_postfix_str(text)
            self.progress_bar.refresh()

        self.test_case_statistics_data_table = self.process_issues(
            on_start=on_start,
            on_iteration=on_iteration,
            on_finish=on_finish
        )

        self.progress_bar.total = 100
        self.progress_bar.n = 100
        self.progress_bar.refresh()
        self.progress_bar.set_postfix_str("Completed")
        self.progress_bar.close()

        return self

    def process_issues(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):

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
        if len(processed_issues) == 0:
            # empty data frame - no tests
            return pd.DataFrame({'Issue Key': [], 'Test Case': [], 'Status': [], 'Execution Status': []})

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
