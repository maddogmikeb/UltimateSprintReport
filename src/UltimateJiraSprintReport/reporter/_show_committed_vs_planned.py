"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template


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
        total_committed_count=self.total_committed[0],
        total_committed_estimate=f"{self.total_committed[1]:.1f}",
        completed_count=self.done.count,
        completed_estimate=f"{self.done.points:.1f}",
        completed_outside_count=self.completed_outside.count,
        completed_outside_estimate=f"{self.completed_outside.points:.1f}",
        total_completed_count=self.done.count + self.completed_outside.count,
        total_completed_estimate=f"{self.done.points + self.completed_outside.points:.1f}",
        in_progress_count=self.in_progress.count,
        in_progress_estimate=f"{self.in_progress.points:.1f}",
        to_do_count=self.to_do.count,
        to_do_estimate=f"{self.to_do.points:.1f}",
        remaining_count=self.in_progress.count + self.to_do.count,
        remaining_estimate=f"{self.in_progress.points + self.to_do.points:.1f}",
        removed_count=self.removed.count,
        removed_estimate=f"{self.removed.points:.1f}",
    )
