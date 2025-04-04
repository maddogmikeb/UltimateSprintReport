# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, protected-access

"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template

def show_report(self):
    """
    Generates the full HTML report for the sprint.

    Returns:
        str: HTML string containing the full sprint report.
    """
    template = Template(
        """
        <html>
        <head>
            <style>
                /* Add your CSS styles here */
            </style>
        </head>
        <body>
            <h1>Ultimate Sprint Report</h1>
            <table id='main-table'>
            <tbody>
                <tr>
                    <td colspan='2'>${sprint_details}</td>
                    <td>${sprint_predictability}</td>
                </tr>
                <tr>
                    <td>${committed_vs_planned_chart}</td>
                    <td>${burndown_chart}</td>
                    <td>${committed_vs_planned}</td>
                </tr>
                <tr>
                    <td colspan='3'>${sprint_issue_types_statistics}</td>
                </tr>
                <tr>
                    <td colspan='3'>${epic_statistics}</td>
                </tr>
                <tr>
                    <td colspan='3'>${predictability}</td>
                </tr>
                ${test_case_statistics_row}
                <tr>
                    <td colspan='3'>${burndown_table}</td>
                </tr>
            </tbody>
            </table>
        </body>
        </html>
        """
    )

    test_case_statistics_template = Template(
        """
        <tr>
            <td colspan='3'>${test_case_statistics}</td>
        </tr>
        """
    )

    if self.test_case_statistics_data_table is not None:
        test_case_statistics_row = test_case_statistics_template.substitute(
            test_case_statistics=self.show_sprint_test_case_statistics()
        )
    else:
        test_case_statistics_row = ""

    return template.substitute(
        sprint_details=self.show_sprint_details(),
        sprint_predictability=self.show_sprint_predictability(),
        committed_vs_planned_chart=self.show_committed_vs_planned_chart(),
        burndown_chart=self.show_burndown_chart(),
        committed_vs_planned=self.show_committed_vs_planned(),
        sprint_issue_types_statistics=self.show_sprint_issue_types_statistics(),
        epic_statistics=self.show_epic_statistics(),
        predictability=self.show_predictability(),
        test_case_statistics_row=test_case_statistics_row,
        burndown_table=self.show_burndown_table(),
    )
