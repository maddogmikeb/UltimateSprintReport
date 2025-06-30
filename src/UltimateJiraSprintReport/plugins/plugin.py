# pylint: disable=import-outside-toplevel, protected-access
# pylint: disable=import-error, unused-import
# pylint: disable=too-few-public-methods, line-too-long
# pylint: disable=missing-function-docstring, invalid-name, missing-module-docstring, missing-class-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements

from operator import itemgetter

from UltimateJiraSprintReport.services._jira_service import JiraService
from UltimateJiraSprintReport.utils._http_utils import parse_url

class Plugin():

    def __init__(self, **kwargs):
        jira_service = itemgetter(
            "jira_service"
        )(kwargs)

        if jira_service is None:
            raise TypeError("'jira_service' argument is missing")

        (
            self.sprint_report_url,
            self.base_url,
            self.project,
            self.rapid_view_id,
            self.sprint_id
        ) = (
            None, None, None, None, None
        )
        self.jira_service = jira_service

    def load(self, **kwargs):
        self.sprint_report_url, self.base_url, self.project, self.rapid_view_id, self.sprint_id = itemgetter(
            "sprint_report_url",
            "base_url",
            "project",
            "board_id",
            "sprint_id"
        )(kwargs)

        if self.sprint_report_url is None:
            if self.base_url is None and self.project is None and self.rapid_view_id is None and self.sprint_id is None:
                raise TypeError("'sprint_report_url' argument is missing and cannot build based on other arguments")
            elif not (self.base_url is None and self.project is None and self.rapid_view_id is None and self.sprint_id is None):
                self.sprint_report_url = f"{self.base_url}jira/software/c/projects/{self.project}/boards/{self.rapid_view_id}/reports/sprint-retrospective?sprint={self.sprint_id}"

        if self.sprint_report_url is None:
            raise TypeError("'sprint_report_url' argument is missing")

        self._set_sprint_details( self.sprint_report_url )

        return self

    def show_report(self):
        pass

    def _set_sprint_details(self, sprint_report_url: str):
        self.sprint_report_url = sprint_report_url
        self.base_url, self.project, self.rapid_view_id, self.sprint_id = parse_url(
            sprint_report_url
        )

        return self
