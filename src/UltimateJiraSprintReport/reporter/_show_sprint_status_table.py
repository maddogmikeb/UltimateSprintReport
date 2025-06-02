"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template

def show_sprint_status_table(self):
    """
    Generates an HTML section displaying sprint status table.

    Returns:
        str: HTML string containing a table of sprint status, e.g. the same as Jira.
    """
    template = Template(
        """
        <style>
            :root {
                --blue-gray: rgba(9, 30, 66, 0.06);
                --yellow: rgb(233, 242, 255); 
                --green: rgb(220, 255, 241);
            }
        </style>
        <h2>Sprint Status</h2>
        <span style='width: 100%; text-align: right;'>* Issues added to sprint after start time</span>
        ${data_table}
    """
    )

    return template.substitute(
        data_table=self.sprint_status_table.to_html(escape=False).replace("NaN", "-")
    )
