"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template


def show_sprint_issue_types_statistics(self):
    """
    Generates an HTML section displaying sprint issue type statistics.

    Returns:
        str: HTML string containing a table of issue type statistics.
    """
    template = Template(
        """
        <h2>Issue Type Statistics</h2>
        ${data_table}
    """
    )

    return template.substitute(
        data_table=self.sprint_issue_types_statistics.to_html()
    )
