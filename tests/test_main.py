import unittest
from src.main import UltimateSprintReport

class TestUltimateSprintReport(unittest.TestCase):

    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"
        self.jira_url = "https://test_jira_instance.atlassian.net"
        self.report = UltimateSprintReport(self.username, self.password, self.jira_url)

    def test_initialization(self):
        self.assertIsInstance(self.report, UltimateSprintReport)

    def test_load_method(self):
        # Assuming load method requires valid parameters
        host = "https://test_jira_instance.atlassian.net/"
        project = "TEST"
        board_id = 1
        sprint_id = 1
        result = self.report.load(host, project, board_id, sprint_id)
        self.assertIsInstance(result, UltimateSprintReport)

if __name__ == '__main__':
    unittest.main()