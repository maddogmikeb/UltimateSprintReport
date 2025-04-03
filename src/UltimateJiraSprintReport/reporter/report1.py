# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long

"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template


def show_login_details(self):
    """
    Generates an HTML table displaying the currently logged-in user's details.

    Returns:
        str: HTML string containing the user's display name and avatar.
    """
    me = self.jira_service.myself()
    template = Template(
        """
        <table>
            <tr>
                <td>Currently logged in as:</td>
                <td>${display_name}</td>
                <td><img src='${avatar_url}' /></td>
            </tr>
        </table>
    """
    )
    return template.substitute(
        display_name=me["displayName"],
        avatar_url=me["avatarUrls"]["32x32"]
    )


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


def show_committed_vs_planned(self):
    """
    Generates an HTML table comparing committed vs planned sprint estimates and issue counts.

    Returns:
        str: HTML string containing the committed vs planned data.
    """
    template = Template(
        """
        <h2>Sprint Estimates & Issue Counts</h2>
        <table>
        <thead>
            <tr>
                <th>Category</th>
                <th>Count</th>
                <th>Estimated</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Total Committed</td>
                <td style='text-align:right'>${total_committed_count}</td>
                <td style='text-align:right'>${total_committed_estimate}</td>
            </tr>
            <tr>
                <td colspan="3"><hr /></td>
            </tr>
            <tr>
                <td>Completed</td>
                <td style='text-align:right'>${completed_count}</td>
                <td style='text-align:right'>${completed_estimate}</td>
            </tr>
            <tr>
                <td>Completed Outside</td>
                <td style='text-align:right'>${completed_outside_count}</td>
                <td style='text-align:right'>${completed_outside_estimate}</td>
            </tr>
            <tr>
                <td><hr /></td>
                <td style='text-align:right'>${total_completed_count}</td>
                <td style='text-align:right'>${total_completed_estimate}</td>
            </tr>
            <tr>
                <td>In Progress</td>
                <td style='text-align:right'>${in_progress_count}</td>
                <td style='text-align:right'>${in_progress_estimate}</td>
            </tr>
            <tr>
                <td>To Do</td>
                <td style='text-align:right'>${to_do_count}</td>
                <td style='text-align:right'>${to_do_estimate}</td>
            </tr>
            <tr>
                <td><hr /></td>
                <td style='text-align:right'>${remaining_count}</td>
                <td style='text-align:right'>${remaining_estimate}</td>
            </tr>
            <tr>
                <td>Removed</td>
                <td style='text-align:right'>${removed_count}</td>
                <td style='text-align:right'>${removed_estimate}</td>
            </tr>
        </tbody>
        </table>
    """
    )
    return template.substitute(
        total_committed_count=self.TotalCommitted[0],
        total_committed_estimate=f"{self.TotalCommitted[1]:.1f}",
        completed_count=self.Done.count,
        completed_estimate=f"{self.Done.points:.1f}",
        completed_outside_count=self.CompletedOutside.count,
        completed_outside_estimate=f"{self.CompletedOutside.points:.1f}",
        total_completed_count=self.Done.count + self.CompletedOutside.count,
        total_completed_estimate=f"{self.Done.points + self.CompletedOutside.points:.1f}",
        in_progress_count=self.InProgress.count,
        in_progress_estimate=f"{self.InProgress.points:.1f}",
        to_do_count=self.ToDo.count,
        to_do_estimate=f"{self.ToDo.points:.1f}",
        remaining_count=self.InProgress.count + self.ToDo.count,
        remaining_estimate=f"{self.InProgress.points + self.ToDo.points:.1f}",
        removed_count=self.Removed.count,
        removed_estimate=f"{self.Removed.points:.1f}",
    )


def show_sprint_details(self):
    """
    Generates an HTML table displaying sprint details such as board name, sprint name, goal, and dates.

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
