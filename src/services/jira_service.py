# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
import json
from atlassian import Jira

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

    def get(self, url: str):
        response = self.jira.request(
            absolute=True,
            method="GET",
            path=f"{self.host}{url}",
        )
        return response.content

    def get_issue(self, key: str, fields: str):
        return self.jira.issue(key=key, fields=fields)

    def jql_query(self, jql: str, fields: str):
        return self.jira.jql(
            jql=jql,
            fields=fields,
        )

    def get_scope_change_burndown_chart(self, rapid_view_id: int, sprint_id: int):
        return json.loads(
            self.get(
                    f"/rest/greenhopper/1.0/rapid/charts/scopechangeburndownchart.json?"
                    f"rapidViewId={rapid_view_id}&"
                    f"sprintId={sprint_id}"
                )
        )

    def get_board_config(self, rapid_view_id: int):
        return json.loads(
            self.get(
                    f"/rest/greenhopper/1.0/rapidviewconfig/editmodel.json?"
                    f"rapidViewId={rapid_view_id}"
                )
        )

    def get_velocity_statistics(self, rapid_view_id: int):
        return json.loads(
            self.get(
                    f"/rest/greenhopper/1.0/rapid/charts/velocity.json/?"
                    f"rapidViewId={rapid_view_id}"
                )
        )

    def get_sprint_report(self, project: str, rapid_view_id: int, sprint_id: int):
        return json.loads(
            self.get(
                f"/jira/software/c/"
                f"projects/{project}"
                f"/boards/{rapid_view_id}"
                f"/reports/sprint-retrospective?"
                f"sprint={sprint_id}"
            )
        )

    def get_status_categories(self):
        return json.loads(
            self.jira.get("/rest/api/2/statuscategory")
        )

    def get_statuses(self):
        return json.loads(
            self.jira.get("/rest/api/2/status")
        )
