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
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements

from collections.abc import Callable

from tqdm.auto import tqdm

import pandas as pd

from .plugins.plugin import Plugin
from .plugins.plugin_register import get_plugin
from .services._jira_service import JiraService
from .utils._http_utils import parse_url


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
            self.committed_vs_planned_chart,
            self.burndown_table,
            self.sprint_report,
            self.removed,
            self.to_do,
            self.in_progress,
            self.done,
            self.completed_outside,
            self.total_committed,
            self.sprint_issue_types_statistics,
            self.sprint_details,
            self.this_sprint_predictability,
            self.predictability_data,
            self.epic_statistics,
            self.velocity_statistics
        ) = (None, None, None, None, None,
             None, None, None, None, None,
             None, None, None, None, None,
             None, None, None, None, None,
             None, None, None, None, None,
             None, None, None, None
            )

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
            self.committed_vs_planned_chart,
            self.burndown_table,
            self.sprint_report,
            self.removed,
            self.to_do,
            self.in_progress,
            self.done,
            self.completed_outside,
            self.total_committed,
            self.sprint_issue_types_statistics,
            self.sprint_details,
            self.this_sprint_predictability,
            self.predictability_data,
            self.epic_statistics,
            self.velocity_statistics
        ) = (None, None, None, None, None,
             None, None, None, None, None,
             None, None, None, None, None,
             None, None, None, None, None,
             None, None, None, None, None,
             None, None, None, None
            )

    from .reporter.reporter import (
        show_burndown_chart,  # pylint: disable=unused-import
        show_burndown_table,  # pylint: disable=unused-import
        show_committed_vs_planned_chart,  # pylint: disable=unused-import
        show_epic_statistics,  # pylint: disable=unused-import
        show_predictability,  # pylint: disable=unused-import
        show_report,  # pylint: disable=unused-import
        show_sprint_predictability,  # pylint: disable=unused-import
        show_committed_vs_planned,  # pylint: disable=unused-import
        show_login_details,  # pylint: disable=unused-import
        show_sprint_details,  # pylint: disable=unused-import
        show_sprint_issue_types_statistics,  # pylint: disable=unused-import
        show_sprint_test_case_statistics  # pylint: disable=unused-import
    )

    def is_connected(self):
        return self.jira_service.is_connected()

    def load_plugin(self, plugin_name, **kwargs) -> Plugin:
        plugin = get_plugin(plugin_name, self.jira_service, **kwargs)
        plugin.load_url(self.sprint_report_url)
        return plugin

    def load(self, project: str, board_id: int, sprint_id: int):
        sprint_url = f"{self.jira_service.host}jira/software/c/projects/{project}/boards/{board_id}/reports/sprint-retrospective?sprint={sprint_id}"
        return self.load_url(sprint_url)

    def load_url(self, sprint_report_url: str):
        """
        Load the sprint report data from the given URL.

        :param sprint_report_url: The URL of the sprint report.
        :return: The UltimateJiraSprintReport instance.
        """

        def on_start(total, text):
            if not total is None:
                self.progress_bar.total = total
            self.progress_bar.set_postfix_str(text)
            self.progress_bar.refresh()

        def on_iteration(text):
            #self.progress_bar.update(1)
            self.progress_bar.set_postfix_str(text)
            self.progress_bar.refresh()

        def on_finish(text):
            #self.progress_bar.n = 100
            self.progress_bar.set_postfix_str(text)
            self.progress_bar.refresh()

        self.progress_bar = tqdm(total=100, desc="Loading Sprint Details", leave=True)
        self.progress_bar.n = 0
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint details")
        self._set_sprint_details(sprint_report_url)
        self.progress_bar.n = round((1 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading status categories")
        self._load_status_categories(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((2 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint report")
        self._load_sprint_report(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((3 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading velocity statistics")
        self._load_velocity_statistics(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((4 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading board configuration")
        self._load_board_config(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((5 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint statistics")
        self._load_sprint_statistics(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((6 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint issue type statistics")
        self._load_sprint_issue_types_statistics(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((6.5 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading committed vs planned chart")
        self._load_committed_vs_planned_chart(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((7 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint details")
        self._calculate_sprint_details(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((8 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading sprint predictability")
        self._calculate_sprint_predictability(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((9 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading epic statistics")
        self._calculate_epic_statistics(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((10 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.set_postfix_str("Loading burndown chart")
        self._load_burndown(on_start=on_start, on_iteration=on_iteration, on_finish=on_finish)
        self.progress_bar.n = round((11 / 11) * 100, 2)
        self.progress_bar.refresh()

        self.progress_bar.n = 100
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

    def _load_status_categories(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):
        on_start(None, "Loading Statuses")
        on_iteration("Loading Status Categories")

        self.status_categories = self.jira_service.get_status_categories()

        on_iteration("Loading Statuses")

        self.statuses = self.jira_service.get_statuses()

        on_finish("Loaded Statuses")

        return self

    def _load_sprint_report(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):
        on_start(None, "Loading Sprint Report")
        self.sprint_report = self.jira_service.get_sprint_report(
            self.rapid_view_id, self.sprint_id
        )
        on_iteration("Loading Sprint Report")
        on_finish("Loaded Sprint Report")
        return self

    def _load_velocity_statistics(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):
        on_start(None, "Loading Velocity Statistics")

        self.velocity_statistics = self.jira_service.get_velocity_statistics(
            self.rapid_view_id
        )

        if (
            "velocityStatEntries" in self.velocity_statistics
            and str(self.sprint_id) in self.velocity_statistics["velocityStatEntries"]
        ):
            on_iteration("Loading Velocity Statistics")
            self.sprint_velocity_statistics = self.velocity_statistics[
                "velocityStatEntries"
            ][str(self.sprint_id)]

        on_finish("Loaded Velocity Statistics")

        return self

    def _load_board_config(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):
        on_start(None, "Loading Board Config")

        self.board_config = self.jira_service.get_board_config(self.rapid_view_id)

        on_iteration("Got Board Config")

        if "name" in self.board_config:
            self.board_name = self.board_config["name"]
        else:
            self.board_name = "Unknown"

        on_finish("Loaded Board Config")
        return self

    def _load_sprint_statistics(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):
        from .functions._sprint_details import load_sprint_statistics

        (
            self.removed,
            self.to_do,
            self.in_progress,
            self.done,
            self.completed_outside,
            self.total_committed,
        ) = load_sprint_statistics(
            self.sprint_report,
            self.sprint_velocity_statistics,
            self.status_categories,
            on_start,
            on_iteration,
            on_finish
        )
        return self

    def _load_sprint_issue_types_statistics(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):
        from .functions._sprint_details import load_sprint_issue_types_statistics

        self.sprint_issue_types_statistics = load_sprint_issue_types_statistics(
            self.sprint_report,
            on_start,
            on_iteration,
            on_finish
        )
        return self

    def _load_committed_vs_planned_chart(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):
        from .functions._sprint_details import load_committed_vs_planned_chart

        image_base64 = load_committed_vs_planned_chart(
            self.removed,
            self.done,
            self.completed_outside,
            self.in_progress,
            self.to_do,
            self.total_committed,
            on_start,
            on_iteration,
            on_finish
        )

        self.committed_vs_planned_chart = f'<img id="committed_vs_planned_chart" class="popupable" src="data:image/png;base64,{image_base64}" alt="Committed vs Planned"/>'

        return self

    def _calculate_sprint_details(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):
        from .functions._sprint_details import calculate_sprint_details

        self.sprint_details = calculate_sprint_details(
            self.board_config,
            self.sprint_report,
            on_start,
            on_iteration,
            on_finish
        )
        return self

    def _calculate_sprint_predictability(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ):
        from .functions._predictability import calculate_predictability

        self.this_sprint_predictability, self.predictability_data = calculate_predictability(
            self.velocity_statistics,
            self.sprint_id,
            self.done.points + self.completed_outside.points,
            self.total_committed[1],
            on_start,
            on_iteration,
            on_finish
        )
        return self

    def _calculate_epic_statistics(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ) -> pd.DataFrame | str:

        from .functions._epic_statistics import calculate_epic_statistics

        self.epic_statistics = calculate_epic_statistics(
            self.jira_service,
            self.board_config,
            self.sprint_report,
            on_start,
            on_iteration,
            on_finish
        )
        return self

    def _load_burndown(
            self,
            on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
            on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
            on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        ) -> pd.DataFrame | str:

        from .functions._burndown import load_burndown

        df, image_base64 = load_burndown(
            self.jira_service,
            self.rapid_view_id,
            self.sprint_id,
            on_start,
            on_iteration,
            on_finish
        )

        self.burndown_table = df
        self.burndown_chart = f'<img id="burndown_chart" class="popupable" src="data:image/png;base64,{image_base64}" alt="Burndown Chart"/>'

        return self
