# pylint: disable=protected-access, wrong-import-position, missing-class-docstring
# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=import-error, import-outside-toplevel, wrong-import-order
# pylint: disable=too-few-public-methods, too-many-arguments, line-too-long

import os
import unittest
import pandas as pd

from __testing__ import Testing
from UltimateJiraSprintReport import UltimateJiraSprintReport

class TestUltimateJiraSprintReport(unittest.TestCase):

    def setUp(self):
        self.username = os.getenv("ATLASSIAN_USERNAME")
        self.password = os.getenv("ATLASSIAN_APIKEY")
        self.host = os.getenv("ATLASSIAN_HOST")
        self.report = UltimateJiraSprintReport(self.username, self.password, self.host)
        self.report.connect()

    def test_initialization(self):
        self.assertIsInstance(self.report, UltimateJiraSprintReport)

    def test_load(self):
        project = 'FDSEWMSR'
        board_id = 364
        sprint_id = 1963
        self.report.load(project, board_id, sprint_id)
        self.assertIsInstance(self.report.burndown_table, pd.DataFrame)
        self.assertIsInstance(self.report.burndown_chart, str)

        if Testing.INTERACTIVE_TESTING_ENABLED:
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                print(self.report.burndown_table)

    def test_status_report_table(self):
        ### Only during development
        if not Testing.INTERACTIVE_TESTING_ENABLED:
            self.skipTest("Not testing interactive tests")
        project = 'FDSEWMSR'
        board_id = 364
        sprint_id = 959
        self.report.load(project, board_id, sprint_id)
        Testing.write_to_temp_html_file_then_open( self.report.show_sprint_status_table() )

    def test_show_report(self):
        ### Only during development
        if not Testing.INTERACTIVE_TESTING_ENABLED:
            self.skipTest("Not testing interactive tests")
        project = 'FDSEWMSR'
        board_id = 364
        sprint_id = 1963
        self.report.load(project, board_id, sprint_id)
        output = self.report.show_report()
        self.assertIsInstance(output, str)
        Testing.write_to_temp_html_file_then_open( output )


if __name__ == '__main__':
    unittest.main()
