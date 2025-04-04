# pylint: disable=protected-access, wrong-import-position, missing-class-docstring
# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=import-error, import-outside-toplevel
# pylint: disable=too-few-public-methods, too-many-arguments

import os
import sys
import unittest
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "src")
sys.path.append(SRC_DIR)

from UltimateJiraSprintReport.UltimateJiraSprintReport import UltimateJiraSprintReport

class TestUltimateJiraSprintReport(unittest.TestCase):

    def setUp(self):
        self.username = os.getenv("ATLASSIAN_USERNAME")
        self.password = os.getenv("ATLASSIAN_APIKEY")
        self.host = os.getenv("ATLASSIAN_HOST")
        self.report = UltimateJiraSprintReport(self.username, self.password, self.host)

    def test_initialization(self):
        self.assertIsInstance(self.report, UltimateJiraSprintReport)
        print(self.report.show_login_details())

    def test_load(self):
        project = 'FDSEWMSR'
        board_id = 364
        sprint_id = 945
        self.report.load(project, board_id, sprint_id)
        self.assertIsInstance(self.report.burndown_table, pd.DataFrame)
        self.assertIsInstance(self.report.burndown_chart, str)

if __name__ == '__main__':
    unittest.main()
