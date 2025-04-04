"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template

link_new_window_template = Template(
    "<a href='${url}' target='_blank'>[${key}] ${summary}</a>"
)

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
