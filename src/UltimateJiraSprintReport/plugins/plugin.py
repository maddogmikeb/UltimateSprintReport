# pylint: disable=import-outside-toplevel, protected-access
# pylint: disable=import-error, unused-import
# pylint: disable=too-few-public-methods, line-too-long
# pylint: disable=missing-function-docstring, invalid-name, missing-module-docstring, missing-class-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements

from UltimateJiraSprintReport.services._jira_service import JiraService
from UltimateJiraSprintReport.utils._http_utils import parse_url

class Plugin():
    def __init__(self, jira_service: JiraService):
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

    def load_url(self, sprint_report_url: str):
        self.sprint_report_url = sprint_report_url
        self._set_sprint_details(sprint_report_url)
        return self

    def load(self):
        return self

    def show_report(self):
        pass

    def _set_sprint_details(self, sprint_report_url: str):
        self.sprint_report_url = sprint_report_url
        self.base_url, self.project, self.rapid_view_id, self.sprint_id = parse_url(
            sprint_report_url
        )
        return self
