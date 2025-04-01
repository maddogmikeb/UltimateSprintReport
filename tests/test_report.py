import unittest
from ultimate_sprint_report.report import UltimateSprintReport

class TestUltimateSprintReport(unittest.TestCase):

    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"
        self.jira_url = "https://test_jira_instance.atlassian.net"
        self.sprint_report = UltimateSprintReport(self.username, self.password, self.jira_url)

    def test_initialization(self):
        self.assertIsInstance(self.sprint_report, UltimateSprintReport)

    def test_load_sprint_report(self):
        # Assuming load method is implemented and works correctly
        host = "https://test_jira_instance.atlassian.net/"
        project = "TEST"
        board_id = 1
        sprint_id = 1
        report = self.sprint_report.load(host, project, board_id, sprint_id)
        self.assertIsInstance(report, UltimateSprintReport)

    def test_load_url(self):
        # Assuming load_url method is implemented and works correctly
        sprint_report_url = "https://test_jira_instance.atlassian.net/jira/software/c/projects/TEST/boards/1/reports/sprint-retrospective?sprint=1"
        report = self.sprint_report.load_url(sprint_report_url)
        self.assertIsInstance(report, UltimateSprintReport)

    # Additional tests for other methods can be added here

if __name__ == '__main__':
    unittest.main()