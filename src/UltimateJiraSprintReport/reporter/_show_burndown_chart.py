# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, protected-access

"""
This module contains functions for generating various sections of an HTML sprint report.
"""


def show_burndown_chart(self):
    """
    Returns the burndown chart for the sprint.

    Returns:
        str: HTML string or object representing the burndown chart.
    """
    if not hasattr(self, "burndown_chart") or self.burndown_chart is None:
        raise ValueError("Burndown chart is not available.")

    return self.burndown_chart
