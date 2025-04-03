# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, protected-access

"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template

link_new_window_template = Template(
    "<a href='${url}' target='_blank'>[${key}] ${summary}</a>"
)


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
    mean_stars = self._calculate_predictability_score_stars(
        total_predictability_score / total if total > 0 else 0
    )

    return template.substitute(
        rows="".join(rows), mean_score=mean_score, mean_stars=mean_stars
    )


def show_sprint_predictability(self):
    """
    Generates an HTML section displaying the sprint predictability rating.

    Returns:
        str: HTML string containing the sprint predictability rating.
    """
    template = Template(
        """
        <h2>Rating: ${stars}</h2>
        """
    )

    if not self.this_sprint_predictability:
        return ""

    return template.substitute(stars=self.this_sprint_predictability["stars"])


def show_epic_statistics(self):
    """
    Generates an HTML table displaying epic statistics within the sprint.

    Returns:
        str: HTML string containing epic statistics.
    """
    template = Template(
        """
        <h2>Epics Within Sprint Statistics</h2>
        <table>
        <thead>
            <tr>
                <th>Parent</th>
                <th>Epic</th>
                <th>Status</th>
                <th>Completed Estimate %</th>
                <th>Completed Count %</th>
            </tr>
        </thead>
        <tbody>
            ${rows}
        </tbody>
        </table>
        """
    )

    row_template = Template(
        """
        <tr>
            <td>${parent}</td>
            <td>${epic_details}</td>
            <td>${status_category}</td>
            <td style='text-align:right'>${completed_pts_perc}</td>
            <td style='text-align:right'>${completed_cnt_perc}</td>
        </tr>
        """
    )

    rows = []
    for epic in sorted(
        self.epic_statistics,
        key=lambda i: (i["parent_summary"] or "") + (i["summary"] or ""),
    ):
        parent = (
            link_new_window_template.substitute(
                url=f"{self.base_url}/browse/{epic['parent_key']}",
                key=epic["parent_key"],
                summary=epic["parent_summary"],
            )
            if epic["parent_key"] is not None
            else "-"
        )
        epic_details = link_new_window_template.substitute(
            url=f"{self.base_url}/browse/{epic['key']}",
            key=epic["key"],
            summary=epic["summary"],
        )
        pts = (
            f"{epic['completed_pts_perc']:.1f}"
            if epic["completed_pts_perc"] is not None
            else "-"
        )
        cnt = (
            f"{epic['completed_cnt_perc']:.1f}"
            if epic["completed_cnt_perc"] is not None
            else "-"
        )
        rows.append(
            row_template.substitute(
                parent=parent,
                epic_details=epic_details,
                status_category=epic["status_category"],
                completed_pts_perc=pts,
                completed_cnt_perc=cnt,
            )
        )

    return template.substitute(rows="".join(rows))


def show_burndown_chart(self):
    """
    Returns the burndown chart for the sprint.

    Returns:
        str: HTML string or object representing the burndown chart.
    """
    if not hasattr(self, "burndown_chart") or not self.burndown_chart:
        raise ValueError("Burndown chart is not available.")

    return self.burndown_chart


def show_burndown_table(self):
    """
    Generates an HTML section displaying the burndown table.

    Returns:
        str: HTML string containing the burndown table.
    """
    if not hasattr(self, "burndown_table") or not self.burndown_table:
        raise ValueError("Burndown table is not available.")

    template = Template(
        """
        <h2>Burndown Table</h2>
        ${table}
        """
    )
    return template.substitute(
        table=self.burndown_table.to_html(escape=False).replace("NaN", "-")
    )


def show_committed_vs_planned_chart(self):
    """
    Returns the committed vs planned chart for the sprint.

    Returns:
        str: HTML string or object representing the committed vs planned chart.
    """
    if (
        not hasattr(self, "committed_vs_planned_chart")
        or not self.committed_vs_planned_chart
    ):
        raise ValueError("Committed vs planned chart is not available.")

    return self.committed_vs_planned_chart


def show_report(self):
    """
    Generates the full HTML report for the sprint.

    Returns:
        str: HTML string containing the full sprint report.
    """
    template = Template(
        """
        <html>
        <head>
            <style>
                /* Add your CSS styles here */
            </style>
        </head>
        <body>
            <h1>Ultimate Sprint Report</h1>
            <table id='main-table'>
            <tbody>
                <tr>
                    <td colspan='2'>${sprint_details}</td>
                    <td>${sprint_predictability}</td>
                </tr>
                <tr>
                    <td>${committed_vs_planned_chart}</td>
                    <td>${burndown_chart}</td>
                    <td>${committed_vs_planned}</td>
                </tr>
                <tr>
                    <td colspan='3'>${sprint_issue_types_statistics}</td>
                </tr>
                <tr>
                    <td colspan='3'>${epic_statistics}</td>
                </tr>
                <tr>
                    <td colspan='3'>${predictability}</td>
                </tr>
                ${test_case_statistics_row}
                <tr>
                    <td colspan='3'>${burndown_table}</td>
                </tr>
            </tbody>
            </table>
        </body>
        </html>
        """
    )

    test_case_statistics_template = Template(
        """
        <tr>
            <td colspan='3'>${test_case_statistics}</td>
        </tr>
        """
    )

    if self.test_case_statistics_data_table is not None:
        test_case_statistics_row = test_case_statistics_template.substitute(
            test_case_statistics=self.show_sprint_test_case_statistics()
        )
    else:
        test_case_statistics_row = ""

    return template.substitute(
        sprint_details=self.show_sprint_details(),
        sprint_predictability=self.show_sprint_predictability(),
        committed_vs_planned_chart=self.show_committed_vs_planned_chart(),
        burndown_chart=self.show_burndown_chart(),
        committed_vs_planned=self.show_committed_vs_planned(),
        sprint_issue_types_statistics=self.show_sprint_issue_types_statistics(),
        epic_statistics=self.show_epic_statistics(),
        predictability=self.show_predictability(),
        test_case_statistics_row=test_case_statistics_row,
        burndown_table=self.show_burndown_table(),
    )
