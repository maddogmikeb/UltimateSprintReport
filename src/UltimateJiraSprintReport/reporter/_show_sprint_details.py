"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template


def show_sprint_details(self):
    """
    Generates an HTML table displaying sprint details such as 
    board name, sprint name, goal, and dates.

    Returns:
        str: HTML string containing sprint details.
    """
    template = Template(
        """
        <h2>Sprint Details</h2>
        <table>
        <tbody>
            <tr>
                <td>Board</td>
                <td>${board_name}</td>
            </tr>
            <tr>
                <td>Sprint Name</td>
                <td><a target='_blank' href='${sprint_report_url}'>${sprint_name}</a></td>
            </tr>
            <tr>
                <td>Sprint Goal</td>
                <td>${sprint_goal}</td>
            </tr>
            <tr>
                <td>Start Date</td>
                <td>${start_date}</td>
            </tr>
            <tr>
                <td>End Date</td>
                <td>${end_date}</td>
            </tr>
            <tr>
                <td>Duration (days)</td>
                <td>${duration_days}</td>
            </tr>
        </tbody>
        </table>
    """
    )
    return template.substitute(
        board_name=self.board_name,
        sprint_report_url=self.sprint_report_url,
        sprint_name=self.sprint_details["name"],
        sprint_goal=self.sprint_details["goal"],
        start_date=self.sprint_details["start_date_string"],
        end_date=self.sprint_details["end_date_string"],
        duration_days=self.sprint_details["duration_days"],
    )
