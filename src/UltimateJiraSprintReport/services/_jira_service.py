# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring

from collections.abc import Callable
from copy import deepcopy
import json

from atlassian import Jira


class JiraService:

    def __init__(self, username: str, password: str, host: str, cache_results: bool=True):
        self.cache_results = cache_results
        self.cache = {}

        if (host is None or len(host) <= 5):
            raise ValueError("Jira scheme URL required")

        if (username is None  or len(username) <= 2):
            raise ValueError("Username required")

        if (password is None or len(password) <= 2):
            raise ValueError("Password required")

        if host[-1] != "/":
            host += "/"

        self.username = username
        self.password = password
        self.host = host
        self.jira = None  # Placeholder for Jira instance

    def clear_cache(self):
        self.cache = {}

    def _get(self, url: str):
        response = self.jira.request(
            absolute=True,
            method="GET",
            path=f"{self.host}{url}",
        )

        return response.content

    def authenticate(self):
        self.jira = Jira(
            url=self.host,
            username=self.username,
            password=self.password,
            cloud=True,
        )

        return self

    def is_connected(self):
        if self.jira is None:
            raise ValueError(
                "Jira instance is not initialized. Call authenticate() first."
            )
        try:
            self.myself()
        except:  # pylint: disable=bare-except
            return False

        return True

    def myself(self):

        return self.jira.myself()

    def check_cache(self, key: str, value_getter: Callable) -> any:
        if not self.cache_results:
            return value_getter()

        cache_key = key
        value = self.cache.get(cache_key) or value_getter()
        self.cache[cache_key] = value

        return value

    def get_issue(self, key: str, fields: str="*all"):

        issue = self.check_cache(
            f"key:{key} fields:{fields}",
            lambda: self.jira.issue(key=key, fields=fields)
        )

        # store it as id as well
        i = deepcopy(issue)
        self.check_cache(f"key:{issue['key']} fields:*all", lambda i=i: i)

        return issue

    def jql_query(self, jql: str, fields: str):

        return self.jira.jql(
            jql=jql,
            fields=fields,
        )

    def get_scope_change_burndown_chart(self, rapid_view_id: int, sprint_id: int):

        return self.check_cache(
            f"scope-change-burndown-chart:{rapid_view_id} {sprint_id}",
            lambda: json.loads(
                self._get(
                    f"rest/greenhopper/1.0/rapid/charts/scopechangeburndownchart.json?"
                    f"rapidViewId={rapid_view_id}&"
                    f"sprintId={sprint_id}"
                )
            )
        )

    def get_board_config(self, rapid_view_id: int):

        return self.check_cache(
            f"board-config:{rapid_view_id} ",
            lambda: json.loads(
                self._get(
                    f"rest/greenhopper/1.0/rapidviewconfig/editmodel.json?"
                    f"rapidViewId={rapid_view_id}"
                )
            )
        )

    def get_velocity_statistics(self, rapid_view_id: int):

        return self.check_cache(
            f"velocity:{rapid_view_id}",
            lambda: json.loads(
                self._get(
                    f"rest/greenhopper/1.0/rapid/charts/velocity.json?"
                    f"rapidViewId={rapid_view_id}"
                )
            )
        )

    def get_sprint_report(self, rapid_view_id: int, sprint_id: int):

        return self.check_cache(
            f"sprint-report:{rapid_view_id} {sprint_id}",
            lambda: json.loads(
                self._get(
                    f"/rest/greenhopper/latest/rapid/charts/sprintreport?"
                    f"rapidViewId={rapid_view_id}&"
                    f"sprintId={sprint_id}"
                )
            )
        )

    def get_status_categories(self):

        return self.check_cache(
            "status-categories",
            lambda: json.loads(
                self._get("rest/api/2/statuscategory")
            )
        )

    def get_statuses(self):

        return self.check_cache(
            "statuses",
            lambda: json.loads(
                self._get("rest/api/2/status")
            )
        )

    def get_sprint_issues(self, sprint_id: int):

        issues = self.check_cache(
            f"sprint-issues: {sprint_id}",
            lambda: json.loads(
                self._get(
                    f"/rest/agile/1.0/sprint/{sprint_id}/issue"
                )
            )
        )['issues']

        # store each issue individually also to improve caching
        for issue in issues:
            i = deepcopy(issue)
            self.check_cache(f"key:{issue['key']} fields:*all", lambda i=i: i)
            self.check_cache(f"key:{issue['id']} fields:*all", lambda i=i: i)

        return issues
