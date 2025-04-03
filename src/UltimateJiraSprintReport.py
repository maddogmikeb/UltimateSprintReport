"""
Defines the `UltimateJiraSprintReport` class, which provides functionality
for generating sprint reports from Jira data. It includes methods for
interacting with Jira, loading plugins, and utilizing various utility
functions for report generation.

Classes:
   - UltimateJiraSprintReport: Main class for generating Jira sprint reports.

"""

# pylint: disable=import-outside-toplevel, protected-access
# pylint: disable=import-error, unused-import
# pylint: disable=too-few-public-methods, line-too-long
# pylint: disable=missing-function-docstring, invalid-name

import pandas as pd

from tqdm.auto import tqdm

from src.services.jira_service import JiraService
from src.utils.http_utils import parse_url


class UltimateJiraSprintReport:
    """
    Main class for generating Jira sprint reports. It provides methods for interacting with Jira,
    loading plugins, and utilizing utility functions for report generation.

    Attributes:
       jira (Jira): Instance of the Jira client for interacting with Jira.
       PluginFolder (str): Path to the folder containing plugins.
       MainModule (str): Name of the main module for plugins.
    """

    def __init__(self, username: str, password: str, jira_scheme_url: str):
        (
            self.jira_service,
            self.sprint_report_url,
            self.base_url,
            self.project,
            self.rapid_view_id,
            self.sprint_id,
            self.board_config,
            self.board_name,
            self.test_case_statistics_data_table,
            self.progress_bar,
            self.sprint_velocity_statistics,
            self.burndown_chart, 
            self.statuses, 
            self.status_categories, 
            self.committed_vs_planned_chart
        ) = (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

        self.jira_service = JiraService(username, password, jira_scheme_url)
        self.jira_service.authenticate()

    def _reset(self):
        (
            self.jira_service,
            self.sprint_report_url,
            self.base_url,
            self.project,
            self.rapid_view_id,
            self.sprint_id,
            self.board_config,
            self.board_name,
            self.test_case_statistics_data_table,
            self.progress_bar,
            self.sprint_velocity_statistics,
            self.burndown_chart, 
            self.statuses, 
            self.status_categories, 
            self.committed_vs_planned_chart
        ) = (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

    def load(self, project: str, board_id: int, sprint_id: int):
        sprint_url = f"{self.jira_service.host}jira/software/c/projects/{project}/boards/{board_id}/reports/sprint-retrospective?sprint={sprint_id}"
        return self.load_url(sprint_url)

    def load_url(self, sprint_report_url: str):
        """
        Load the sprint report data from the given URL.

        :param sprint_report_url: The URL of the sprint report.
        :return: The UltimateJiraSprintReport instance.
        """

        self.progress_bar = tqdm(total=100, desc="Loading Sprint Details", leave=True)
        self.progress_bar.n = 0
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint details")
        self._set_sprint_details(sprint_report_url)
        self.progress_bar.n = round((1 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading status categories")
        self._load_status_categories()
        self.progress_bar.n = round((2 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint report")
        self._load_sprint_report()
        self.progress_bar.n = round((3 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading velocity statistics")
        self._load_velocity_statistics()
        self.progress_bar.n = round((4 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading board configuration")
        self._load_board_config()
        self.progress_bar.n = round((5 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint statistics")
        self._load_sprint_statistics()
        self.progress_bar.n = round((6 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint issue type statistics")
        self._load_sprint_issue_types_statistics()
        self.progress_bar.n = round((6.5 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading committed vs planned chart")
        self._load_committed_vs_planned_chart()
        self.progress_bar.n = round((7 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint details")
        self._calculate_sprint_details()
        self.progress_bar.n = round((8 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint predictability")
        self._calculate_sprint_predictability()
        self.progress_bar.n = round((9 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading epic statistics")
        self._calculate_epic_statistics()
        self.progress_bar.n = round((10 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading burndown chart")
        self._load_burndown()
        self.progress_bar.n = round((11 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Completed")
        self.progress_bar.close()
        return self

    def _set_sprint_details(self, sprint_report_url: str):
        self.sprint_report_url = sprint_report_url
        self.base_url, self.project, self.rapid_view_id, self.sprint_id = parse_url(
            sprint_report_url
        )
        self.board_config = self.jira_service.get_board_config(self.rapid_view_id)
        self.board_name = (
            self.board_config["name"] if "name" in self.board_config else "Unknown"
        )
        return self

    def _load_status_categories(self):
        self.status_categories = self.jira_service.get_status_categories()
        self.statuses = self.jira_service.get_statuses()
        return self

    def _load_sprint_report(self):
        self.sprint_report = self.jira_service.get_sprint_report(
            self.project, self.rapid_view_id, self.sprint_id
        )
        return self

    def _load_velocity_statistics(self):
        self.velocity_statistics = self.jira_service.get_velocity_statistics(
            self.rapid_view_id
        )
        if (
            "velocityStatEntries" in self.velocity_statistics
            and str(self.sprint_id) in self.velocity_statistics["velocityStatEntries"]
        ):
            self.sprint_velocity_statistics = self.velocity_statistics[
                "velocityStatEntries"
            ][str(self.sprint_id)]
        return self

    def _load_board_config(self):
        self.board_config = self.jira_service.get_board_config(self.rapid_view_id)
        if "name" in self.board_config:
            self.board_name = self.board_config["name"]
        else:
            self.board_name = "Unknown"
        return self

    def _load_sprint_statistics(self):
        from src.functions.sprint_details import load_sprint_statistics
        
        (
            self.removed,
            self.to_do,
            self.in_progress,
            self.done,
            self.completed_outside,
            self.total_committed,
        ) = load_sprint_statistics(
            self.sprint_report, self.sprint_velocity_statistics, self.status_categories
        )
        return self

    def _load_sprint_issue_types_statistics(self):
        from src.functions.sprint_details import load_sprint_issue_types_statistics

        self.sprint_issue_types_statistics = load_sprint_issue_types_statistics(self.sprint_report)
        return self

    def _load_committed_vs_planned_chart(self):
        from src.functions.sprint_details import load_committed_vs_planned_chart

        image_base64 = load_committed_vs_planned_chart(
            self.removed,
            self.done,
            self.completed_outside,
            self.in_progress,
            self.to_do,
            self.total_committed
        )

        self.committed_vs_planned_chart = f'<img id="committed_vs_planned_chart" class="popupable" src="data:image/png;base64,{image_base64}" alt="Committed vs Planned"/>'

        return self

    def _calculate_sprint_details(self):
        from src.functions.sprint_details import calculate_sprint_details

        self.sprint_details = calculate_sprint_details(self.board_config, self.sprint_report)
        return self

    def _calculate_sprint_predictability(self):
        from src.functions.predictability import calculate_predictability

        self.this_sprint_predictability, self.predictability_data = calculate_predictability(
            self.velocity_statistics,
            self.sprint_id,
            self.done.points + self.completed_outside.points,
            self.total_committed[1],            
        )
        return self

    def _calculate_epic_statistics(self) -> pd.DataFrame | str:
        from src.functions.epic_statistics import calculate_epic_statistics
 
        self.epic_statistics = calculate_epic_statistics(
            self.jira_service,
            self.board_config,
            self.sprint_report
        )
        return self

    def _load_burndown(self) -> pd.DataFrame | str:
        from src.functions.burndown import load_burndown

        df, image_base64 = load_burndown(
            self.jira_service,
            self.rapid_view_id,
            self.sprint_id,
        )

        self.burndown_table = df
        self.burndown_chart = f'<img id="burndown_chart" class="popupable" src="data:image/png;base64,{image_base64}" alt="Burndown Chart"/>'

        return self
