"""
This module contains functions for generating various sections of an HTML sprint report.
"""


def show_committed_vs_planned_chart(self):
    """
    Returns the committed vs planned chart for the sprint.

    Returns:
        str: HTML string or object representing the committed vs planned chart.
    """
    if (
        not hasattr(self, "committed_vs_planned_chart")
        or self.committed_vs_planned_chart is None
    ):
        raise ValueError("Committed vs planned chart is not available.")

    return self.committed_vs_planned_chart
