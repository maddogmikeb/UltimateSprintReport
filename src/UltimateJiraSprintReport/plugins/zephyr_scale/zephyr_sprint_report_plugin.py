# pylint: disable=import-outside-toplevel, protected-access
# pylint: disable=import-error, unused-import, wrong-import-order
# pylint: disable=too-few-public-methods, line-too-long
# pylint: disable=missing-function-docstring, invalid-name, missing-module-docstring, missing-class-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements

from collections.abc import Callable
from operator import itemgetter
from string import Template
import warnings

from tqdm.auto import tqdm

from UltimateJiraSprintReport.plugins.plugin_register import Plugin
from UltimateJiraSprintReport.plugins.zephyr_scale.services.zephyr_scale_api_service import ZephyrScaleApiService
from UltimateJiraSprintReport.plugins.zephyr_scale.utils._pandas_utils import make_testcase_clickable,\
    make_testcycle_clickable
from UltimateJiraSprintReport.services._jira_service import JiraService
from UltimateJiraSprintReport.utils._pandas_utils import make_clickable
import numpy as np
import pandas as pd


def flatten(xss):

    return [x for xs in xss for x in xs]


class ZephyrSprintReportPlugin(Plugin):

    def __init__(self, **kwargs):

        jira_service, zephyr_api = itemgetter(
            "jira_service",
            "zephyr_api"
        )(kwargs)

        super().__init__(jira_service)
        self.zephyr_service = ZephyrScaleApiService(zephyr_api)

        (
            self.progress_bar,
            self.test_case_statistics_data_table,
            self.test_cycle_details,
            self.test_cycle_test_cases_data_table
         ) = (
            None, None, None, None
        )

    def load(self, **kwargs):

        super().load(**kwargs)

        self.progress_bar = tqdm(total=100, desc="Loading Test Case Details", leave=True)
        self.progress_bar.n = 0
        self.progress_bar.refresh()

        def on_start(total, text):
            if not total is None:
                if self.progress_bar.total > 0:
                    self.progress_bar.total = self.progress_bar.total + total
                else:
                    self.progress_bar.total = total
            if self.progress_bar.postfix != text:
                self.progress_bar.set_postfix_str(text, refresh=True)

        def on_iteration(text):
            self.progress_bar.update(1)
            if self.progress_bar.postfix != text:
                self.progress_bar.set_postfix_str(text, refresh=True)

        def on_finish(text):
            if self.progress_bar.postfix != text:
                self.progress_bar.set_postfix_str(text, refresh=True)

        self.test_case_statistics_data_table = self.process_issues(
            on_start=on_start,
            on_iteration=on_iteration,
            on_finish=on_finish
        )

        self.test_cycle_details, self.test_cycle_test_cases_data_table = self.process_test_cycle(
            on_start=on_start,
            on_iteration=on_iteration,
            on_finish=on_finish
        )

        if self.test_case_statistics_data_table is not None and self.test_cycle_test_cases_data_table is not None:
            # merge the test_case_statistics_data_table and the test_cycle and identify the duplicates
            not_in_cycle = pd.merge(
                self.test_case_statistics_data_table,
                self.test_cycle_test_cases_data_table,
                how='outer',
                indicator=True
            ).query('_merge=="left_only"').drop('_merge', axis=1)

            not_in_cycle['Issue Key'] = "*" + not_in_cycle['Issue Key']

            df = pd.concat([not_in_cycle, self.test_cycle_test_cases_data_table])
            df = df.sort_values(by=['Execution Status'], ascending=False).reset_index(drop=True)

            self.test_case_statistics_data_table = None # we dont need this anymore
            self.test_cycle_test_cases_data_table = df

        self.progress_bar.n = self.progress_bar.total
        self.progress_bar.refresh()
        self.progress_bar.set_postfix_str("Completed")
        self.progress_bar.close()

        return self

    def process_test_cycle(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):

        on_start(None, "Searching for test cycle linked to sprint report")

        def _filter(test_cycle):
            on_iteration(f"Checking test cycle: {test_cycle['key'] if 'key' in test_cycle else test_cycle}")

            if 'links' in test_cycle and 'webLinks' in test_cycle['links']:
                for link in test_cycle['links']['webLinks']:
                    if link['url'].startswith(self.sprint_report_url):
                        return True

            return False

        test_cycle = self.zephyr_service.get_test_cycle_filter(_filter)

        if test_cycle is None:
            warnings.warn("WARNING: No test cycle linked to sprint, add sprint url to test cycle web links")
            return None, None

        if 'links' not in test_cycle or 'issues' not in test_cycle['links']:
            raise ValueError("Test cycle has no links")

        test_cycle['status'] = self.zephyr_service.get_test_case_status(test_cycle['status']['self'])
        test_cycle['project'] = self.zephyr_service.get_project(test_cycle['project']['self'])
        test_cycle['folder'] = self.zephyr_service.get_folder(test_cycle['folder']['self'])

        test_executions = self.zephyr_service.get_test_cycle_test_executions(test_cycle['key'])

        test_cases = []

        for test_execution in test_executions:
            if 'testCase' in test_execution and 'self' in test_execution['testCase']:
                test_case = self.zephyr_service.get_test_case(test_execution['testCase']['self'])

                test_case['status'] = self.zephyr_service.get_test_case_status(test_case['status']['self'])

                lastExec = self.zephyr_service.get_test_case_latest_executions(test_case['key'])
                if lastExec and 'values' in lastExec and len(lastExec['values']) == 1:
                    test_case['lastExecution'] = lastExec['values'][0]
                    test_case['lastExecution']['testExecutionStatus'] = self.zephyr_service.get_test_case_execution_status(
                        test_case['lastExecution']['testExecutionStatus']['self']
                    )
                else:
                    test_case['lastExecution'] = None

                issues = []
                if 'links' in test_cycle and 'issues' in test_case['links']:
                    for link in test_case['links']['issues']:
                        if 'issueId' in link:
                            issues.append(self.jira_service.get_issue(link['issueId']))

                test_case['issues'] = issues

                test_cases.append(test_case)

        on_finish("Completed checking test cycles")

        test_cycle_df = pd.DataFrame([{
            "Key": make_testcycle_clickable(test_cycle['key'], self.base_url, self.project) ,
            "Name": test_cycle['name'],
            "Project": test_cycle['project']['key'],
            "Status": test_cycle['status']['name'],
            "Folder": test_cycle['folder']['name'],
            "Description": test_cycle['description'],
            "Start": test_cycle['plannedStartDate'],
            "End": test_cycle['plannedEndDate'],
        }]).T

        df = pd.DataFrame([{
            "Issue Key": tc['issues'][0]['key'] if len(tc['issues']) == 1 else "Unknown",
            "Test Case": tc['key'],
            "Issue Status": tc['issues'][0]['fields']['status']['name'] if len(tc['issues']) == 1 else "Unknown",
            "Status": tc['status']['name'],
            "Execution Status": tc['lastExecution']['testExecutionStatus']['name']
        } for tc in test_cases])

        df["Issue Key"] = df["Issue Key"].apply(lambda x: make_clickable(x, self.base_url))
        df["Test Case"] = df["Test Case"].apply(lambda x: make_testcase_clickable(x, self.base_url, self.project))
        df = df.groupby(['Issue Key', 'Issue Status'], as_index=False).agg({
            'Test Case': lambda x: ', '.join(x.sort_values()) if len(x) > 0 else 'No Test Cases',
            'Status': lambda x: (x == 'Approved').sum() / len(x),
            'Execution Status': lambda x: (x == 'Pass').sum() / len(x)
        })
        df = df.sort_values(by=['Execution Status'], ascending=False).reset_index(drop=True)

        return test_cycle_df, df

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

        for issue in issues:
            processed_issues.append(process_issue(issue))
            on_iteration(f"Processed: {issue['key']}")

        processed_issues = flatten(processed_issues)
        if len(processed_issues) == 0:
            # empty data frame - no tests
            on_finish("Done")
            return pd.DataFrame({'Issue Key': [], 'Test Case': [], 'Status': [], 'Execution Status': []})

        df = pd.DataFrame(processed_issues)
        df["Issue Key"] = df["Issue Key"].apply(lambda x: make_clickable(x, self.base_url))
        df["Test Case"] = df["Test Case"].apply(lambda x: make_testcase_clickable(x, self.base_url, self.project))
        df = df.groupby(['Issue Key', 'Issue Status'], as_index=False).agg({
            'Test Case': lambda x: ', '.join(x.sort_values()) if len(x) > 0 else 'No Test Cases',
            'Status': lambda x: (x == 'Approved').sum() / len(x),
            'Execution Status': lambda x: (x == 'Pass').sum() / len(x)
        })
        df = df.sort_values(by=['Execution Status'], ascending=False).reset_index(drop=True)

        on_finish("Done")

        return df

    def show_test_cycle_statistics(self):
        template = Template(
            """
            <h2>Sprint Test Cycle Details</h2>
            ${test_cycle_details}
            <h3>Sprint Test Cycle - Test Cases</h3>
            Note: * indicates tests executed on issues within sprint but not added to test cycle.
            ${test_cycle_data_table}
            """
        )

        if self.test_cycle_details is None:
            return "No sprint report linked (via web links) to test cycle. Add the sprint report url to the test cycle links to link items."

        df = self.test_cycle_test_cases_data_table
        df.loc['Total'] = df.mean(numeric_only=True, axis=0)
        df.loc['Total'] = df.loc['Total'].replace(np.nan, '', regex=True)
        df['Status'] = df['Status'].apply(lambda x: f"{x:.1%}")
        df['Execution Status'] = df['Execution Status'].apply(lambda x: f"{x:.1%}")

        return template.substitute(
            test_cycle_details= self.test_cycle_details.to_html(escape=False).replace("NaN", "-"),
            test_cycle_data_table= df.to_html(escape=False).replace("NaN", "-")
        )

    def show_test_case_statistics(self):
        template = Template(
            """
            <h2>Sprint Test Case Statistics</h2>
            ${test_case_statistics_data_table}
            """
        )

        if self.test_case_statistics_data_table is None:
            return ""

        df = self.test_case_statistics_data_table
        df.loc['Total'] = df.mean(numeric_only=True, axis=0)
        df.loc['Total'] = df.loc['Total'].replace(np.nan, '', regex=True)
        try:
            df['Status'] = df['Status'].apply(lambda x: f"{x:.1%}")
        except: #pylint: disable=bare-except
            pass
        try:
            df['Execution Status'] = df['Execution Status'].apply(lambda x: f"{x:.1%}")
        except: #pylint: disable=bare-except
            pass

        return template.substitute(
            test_case_statistics_data_table= df.to_html(escape=False).replace("NaN", "-")
        )

    def show_report(self):

        template = Template(
            """
            <table>
               <tr>
                    <td>${test_cycle_statistics}</td>
                </tr>
                <tr>
                    <td>${test_case_statistics}</td>
                </tr>
             </table>
            """
        )

        return template.substitute(
            test_case_statistics=self.show_test_case_statistics(),
            test_cycle_statistics=self.show_test_cycle_statistics()
        )
