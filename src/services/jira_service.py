import json 
from atlassian import Jira

class JiraService:
    def __init__(self, username: str, password: str, jira_url: str):
        self.username = username
        self.password = password
        self.jira_url = jira_url
        self.jira = None  # Placeholder for Jira instance

    def authenticate(self):       
        self.jira = Jira(url=self.jira_url, username=self.username, password=self.password, cloud=True)

    def load_sprint_report(self, project: str, board_id: int, sprint_id: int):
        sprint_url = f"{self.jira_url}/jira/software/c/projects/{project}/boards/{board_id}/reports/sprint-retrospective?sprint={sprint_id}"
        return self._load_url(sprint_url)

    def _load_url(self, url: str):
        response = self.jira.request(absolute=True, method="GET", path=url)
        return response.content

    def get_issue(self, issue_key: str):
        return self.jira.issue(key=issue_key)

    def jql_query(self, jql: str, fields: str):
        return self.jira.jql(jql=jql, fields=fields)
    
    def get_scope_change_burndown_chart(self, base_url:str, rapidViewId: int , sprintId: int):
        return json.loads(
			self.jira.request(
				absolute=True,
				method="GET",
				path="{base_url}{path}?rapidViewId={rapidViewId}&sprintId={sprintId}".format(
					base_url=base_url,
					path="/rest/greenhopper/1.0/rapid/charts/scopechangeburndownchart.json",
					rapidViewId=rapidViewId,
					sprintId=sprintId,
				),
			).content
		)
    
    def get_board_config(self, base_url:str, rapidViewId: int):
        return json.loads(
			self.jira.request(
				absolute=True,
				method="GET",
				path="{base_url}{path}?rapidViewId={rapidViewId}".format(
					base_url=base_url,
					path="/rest/greenhopper/1.0/rapidviewconfig/editmodel.json",
					rapidViewId=rapidViewId,
				),
			).content
		)