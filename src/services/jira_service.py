import json
from atlassian import Jira

## Just while developing
# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring

class JiraService:
    def __init__(self, username: str, password: str, host: str):
        if (host is None) or (username is None) or (password is None):
            raise ValueError("Jira scheme URL, username and password are required")

        self.username = username
        self.password = password
        self.host = host
        self.jira = None  # Placeholder for Jira instance

    def authenticate(self):
        self.jira = Jira(
            url=self.host,
            username=self.username,
            password=self.password,
            cloud=True,
        )

    def is_connected(self):
        if self.jira is None:
            raise ValueError("Jira instance is not initialized. Call authenticate() first.")
        try:
            self.jira.myself()
            return True
        except: # pylint: disable=bare-except
            return False

    def load_sprint_report(self, project: str, board_id: int, sprint_id: int):
        sprint_url = (
            f"{self.host}/jira/software/c/projects/{project}/boards/{board_id}/"
            f"reports/sprint-retrospective?sprint={sprint_id}"
        )
        return self._load_url(sprint_url)

    def _load_url(self, url: str):
        response = self.jira.request(
            absolute=True,
            method="GET",
            path=url,
        )
        return response.content

    def get_issue(self, issue_key: str):
        return self.jira.issue(key=issue_key)

    def jql_query(self, jql: str, fields: str):
        return self.jira.jql(
            jql=jql,
            fields=fields,
        )

    def get_scope_change_burndown_chart(self, rapid_view_id: int, sprint_id: int):
        return json.loads(
            self.jira.request(
                absolute=True,
                method="GET",
                path=(
                    f"{self.host}/rest/greenhopper/1.0/rapid/charts/"
                    f"scopechangeburndownchart.json?rapidViewId={rapid_view_id}&"
                    f"sprintId={sprint_id}"
                ),
            ).content
        )

    def get_board_config(self, rapid_view_id: int):
        return json.loads(
            self.jira.request(
                absolute=True,
                method="GET",
                path=(
                    f"{self.host}/rest/greenhopper/1.0/rapidviewconfig/"
                    f"editmodel.json?rapidViewId={rapid_view_id}"
                ),
            ).content
        )
