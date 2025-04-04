# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, protected-access

"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template

def show_sprint_test_case_statistics(self):
    """
    Generates an HTML section displaying sprint test case statistics.

    Returns:
        str: HTML string containing a table of test case statistics.
    """
    template = Template(
        """
        <h2>Sprint Test Case Statistics</h2>
        ${data_table}
    """
    )
    return template.substitute(
        data_table=self.test_case_statistics_data_table.to_html(escape=False).replace(
            "NaN", "-"
        )
    )
