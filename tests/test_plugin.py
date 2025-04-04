# pylint: disable=protected-access, wrong-import-position, missing-class-docstring
# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=import-error, import-outside-toplevel, line-too-long
# pylint: disable=too-few-public-methods, too-many-arguments

import os
import sys
import unittest

import pandas as pd

from UltimateJiraSprintReport.UltimateJiraSprintReport import UltimateJiraSprintReport
from UltimateJiraSprintReport.plugins.zephyr_scale.zephyr_sprint_report_plugin import ZephyrSprintReportPlugin

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "src")
sys.path.append(SRC_DIR)


class TestPlugin(unittest.TestCase):

    def setUp(self):
        self.username = os.getenv("ATLASSIAN_USERNAME")
        self.password = os.getenv("ATLASSIAN_APIKEY")
        self.host = os.getenv("ATLASSIAN_HOST")
        self.zephyr_scale_api_key = os.getenv("ZEPHYR_SCALE_APIKEY")
        self.report = UltimateJiraSprintReport(self.username, self.password, self.host)

    def test_initialization(self):
        self.assertIsInstance(self.report, UltimateJiraSprintReport)
        print(self.report.show_login_details())

    def test_show_report(self):
        project = 'FDSEWMSR'
        board_id = 364
        sprint_id = 946
        self.report.load(project, board_id, sprint_id)

        zephyr_plugin = self.report.load_plugin("zephyr_scale", zephyr_api=self.zephyr_scale_api_key)
        self.assertIsInstance(zephyr_plugin, ZephyrSprintReportPlugin)

        zephyr_plugin.load()
        self.assertIsInstance(zephyr_plugin.test_case_statistics_data_table, pd.DataFrame)

        output = zephyr_plugin.show_report()
        self.assertIsInstance(output, str)
        print(output)


if __name__ == '__main__':
    unittest.main()
