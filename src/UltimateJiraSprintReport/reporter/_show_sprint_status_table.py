# pylint: disable=line-too-long

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
            .dataframe {
                width: 100%;
            }
        </style>
        <h2>Sprint Status</h2>
        <span style='width: 100%; text-align: right;'>
            * Issues added to sprint after start time
        </span>
        ${html}
    """
    )

    html = ""
    completed_issues = self.sprint_status_table[self.sprint_status_table["Type"] == "Completed Issues"].reset_index(drop=True)
    if (len(completed_issues.index)) > 0:
        story_points = str(completed_issues["Original Estimate"].sum()) + "→" + str(completed_issues["Current Estimate"].sum()) if completed_issues["Estimate"].apply(str).str.contains("→").any() else str(completed_issues["Current Estimate"].sum())
        completed_issues = completed_issues.drop(["Type", "Original Estimate", "Current Estimate"], axis=1)
        completed_issues.index = completed_issues.index + 1
        html += "<h2>Completed Issues</h2><div>Estimate: " + story_points + "</div>" + completed_issues.to_html(escape=False).replace("NaN", "-")

    issues_not_completed_in_current_sprint = self.sprint_status_table[self.sprint_status_table["Type"] == "Issues Not Completed"].reset_index(drop=True)
    if (len(issues_not_completed_in_current_sprint.index)) > 0:
        story_points = str(issues_not_completed_in_current_sprint["Original Estimate"].sum()) + "→" + str(issues_not_completed_in_current_sprint["Current Estimate"].sum()) if issues_not_completed_in_current_sprint["Estimate"].apply(str).str.contains("→").any() else str(issues_not_completed_in_current_sprint["Current Estimate"].sum())
        issues_not_completed_in_current_sprint = issues_not_completed_in_current_sprint.drop(["Type", "Original Estimate", "Current Estimate"], axis=1)
        issues_not_completed_in_current_sprint.index = issues_not_completed_in_current_sprint.index + 1
        html += "<h2>Issues Not Completed</h2><div>Estimate: " + story_points + "</div>" + issues_not_completed_in_current_sprint.to_html(escape=False).replace("NaN", "-")

    issues_completed_in_another_sprint = self.sprint_status_table[self.sprint_status_table["Type"] == "Issues completed outside of this sprint"].reset_index(drop=True)
    if (len(issues_completed_in_another_sprint.index)) > 0:
        story_points = str(issues_completed_in_another_sprint["Original Estimate"].sum()) + "→" + str(issues_completed_in_another_sprint["Current Estimate"].sum()) if issues_completed_in_another_sprint["Estimate"].apply(str).str.contains("→").any() else str(issues_completed_in_another_sprint["Current Estimate"].sum())
        issues_completed_in_another_sprint = issues_completed_in_another_sprint.drop(["Type", "Original Estimate", "Current Estimate"], axis=1)
        issues_completed_in_another_sprint.index = issues_completed_in_another_sprint.index + 1
        html += "<h2>Issues completed outside of this sprint</h2><div>Estimate: " + story_points + "</div>" + issues_completed_in_another_sprint.to_html(escape=False).replace("NaN", "-")

    punted_issues = self.sprint_status_table[self.sprint_status_table["Type"] == "Issues Removed From Sprint"].reset_index(drop=True)
    if (len(punted_issues.index)) > 0:
        story_points = str(punted_issues["Original Estimate"].sum()) + "→" + str(punted_issues["Current Estimate"].sum()) if punted_issues["Estimate"].apply(str).str.contains("→").any() else str(punted_issues["Current Estimate"].sum())
        punted_issues = punted_issues.drop(["Type", "Original Estimate", "Current Estimate"], axis=1)
        punted_issues.index = punted_issues.index + 1
        html += "<h2>Issues Removed From Sprint</h2><div>Estimate: " + story_points + "</div>" + punted_issues.to_html(escape=False).replace("NaN", "-")

    return template.substitute(
        html=html
    )
