# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, protected-access

"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template
from ..utils._predictability_utils import calculate_predictability_score_stars

def show_predictability(self):
    """
    Generates an HTML table displaying predictability statistics.

    Returns:
        str: HTML string containing predictability statistics.
    """
    template = Template(
        """
        <h2>Predictability Statistics</h2>
        <table>
        <thead>
            <tr>
                <th>Sprint</th>
                <th>Estimated</th>
                <th>Completed</th>
                <th>Predictability Score</th>
                <th>Stars</th>
            </tr>
        </thead>
        <tbody>
            ${rows}
            <tr>
                <td colspan="3" style='font-weight: bold'>Average</td>
                <td style='font-weight: bold; text-align:right'>${mean_score}</td>
                <td style='font-weight: bold; text-align:right'>${mean_stars}</td>
            </tr>
        </tbody>
        </table>
        """
    )

    row_template = Template(
        """
        <tr>
            <td>${name}</td>
            <td style='text-align:right'>${estimated_points}</td>
            <td style='text-align:right'>${completed_points}</td>
            <td style='text-align:right'>${predictability_score}</td>
            <td style='text-align:right'>${stars}</td>
        </tr>
        """
    )

    rows = []
    total_predictability_score = 0
    total = 0
    for data in self.predictability_data:
        predictability_score = (
            f"{data['predictability_score']:.2f}"
            if data["predictability_score"] is not None
            else "-"
        )
        if data["predictability_score"] is not None:
            total_predictability_score += data["predictability_score"]
            total += 1

        rows.append(
            row_template.substitute(
                name=data["name"],
                estimated_points=data["estimated_points"],
                completed_points=data["completed_points"],
                predictability_score=predictability_score,
                stars=data["stars"],
            )
        )

    mean_score = f"{total_predictability_score / total:.2f}" if total > 0 else "-"
    mean_stars = calculate_predictability_score_stars(
        total_predictability_score / total if total > 0 else 0
    )

    return template.substitute(
        rows="".join(rows), mean_score=mean_score, mean_stars=mean_stars
    )
