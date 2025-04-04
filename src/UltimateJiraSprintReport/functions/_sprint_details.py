# pylint: disable=missing-module-docstring, missing-function-docstring, line-too-long
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments

import base64
import io
from datetime import datetime
from collections.abc import Callable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from ..models._data_point import DataPoint

def _calculate_estimates(sprint_report, status_category_id) -> tuple[int, int]:
    count = 0
    estimate = 0

    if not sprint_report or len(sprint_report) == 0:
        raise ValueError("Sprint Report not loaded")

    for issue in sprint_report["contents"]["issuesNotCompletedInCurrentSprint"]:
        if issue["status"]["statusCategory"]["id"] == status_category_id:
            count += 1
            estimate += issue["estimateStatistic"]["statFieldValue"].get("value", 0)

    return count, estimate

def _get_status_category_id(status_categories, name) -> str:
    return str(next(x["id"] for x in status_categories if x["name"] == name))

def load_sprint_issue_types_statistics(sprint_report) -> pd.DataFrame:
    issue_types = {}

    for stat_type in [
        "completedIssues",
        "issuesNotCompletedInCurrentSprint",
        "puntedIssues",
        "issuesCompletedInAnotherSprint",
    ]:
        for issue in sprint_report["contents"][stat_type]:
            if issue["typeName"] not in issue_types:
                issue_types[issue["typeName"]] = {}
            if stat_type not in issue_types[issue["typeName"]]:
                issue_types[issue["typeName"]][stat_type] = 0
            issue_types[issue["typeName"]][stat_type] += 1

    df = pd.DataFrame(issue_types)
    df = df.fillna("-").infer_objects()
    df_transposed = df.T
    new_cols = []

    if "completedIssues" in df_transposed.columns:
        new_cols.append("Completed")
    if "issuesCompletedInAnotherSprint" in df_transposed.columns:
        new_cols.append("Completed Outside")
    if "issuesNotCompletedInCurrentSprint" in df_transposed.columns:
        new_cols.append("Not Completed")
    if "puntedIssues" in df_transposed.columns:
        new_cols.append("Removed")

    df_transposed.columns = new_cols
    df_transposed = df_transposed.map(
        lambda x: int(x) if isinstance(x, float) else x
    )

    return df_transposed

def load_sprint_statistics(sprint_report, sprint_velocity_statistics, status_categories) -> tuple[DataPoint, DataPoint, DataPoint, DataPoint, DataPoint, tuple[int, int]]:

    if not sprint_report:
        raise ValueError("Sprint Report not loaded")

    to_do_key_id = _get_status_category_id(status_categories, "To Do")
    in_progress_key_id = _get_status_category_id(status_categories, "In Progress")

    to_do_count, to_do_estimate = _calculate_estimates(sprint_report, to_do_key_id)
    in_progress_count, in_progress_estimate = _calculate_estimates(sprint_report, in_progress_key_id)

    removed_points = (
        -sprint_report["contents"]
        .get("puntedIssuesEstimateSum", {})
        .get("value", 0)
    )

    if removed_points in (0, -0):
        removed_points = 0

    removed = DataPoint(
        "Removed",
        -len(sprint_report["contents"]["puntedIssues"]),
        removed_points,
        "#d04437",
        None,
        "#ccc",
    )

    to_do = DataPoint(
        "ToDo", to_do_count, to_do_estimate, "#091E420F", None, "#44546F"
    )

    in_progress = DataPoint(
        "InProgress", in_progress_count, in_progress_estimate, "#deebff", None, "#0055CC"
    )

    done = DataPoint(
        "Completed",
        len(sprint_report["contents"]["completedIssues"]),
        sprint_report["contents"]
        .get("completedIssuesEstimateSum", {})
        .get("value", 0),
        "#e3fcef",
        None,
        "#216E4E",
    )

    completed_outside = DataPoint(
        "Completed Outside",
        len(sprint_report["contents"]["issuesCompletedInAnotherSprint"]),
        sprint_report["contents"]
        .get("issuesCompletedInAnotherSprintEstimateSum", {})
        .get("value", 0),
        "#e3fcef",
        "X",
        "#216E4E",
    )

    if sprint_velocity_statistics:
        total_committed = [
            len(sprint_velocity_statistics["allConsideredIssueKeys"]),
            sprint_velocity_statistics["estimated"].get("value", 0),
        ]
    else:
        total_committed = [
            len(sprint_report["contents"]["completedIssues"])
            + len(
                sprint_report["contents"]["issuesNotCompletedInCurrentSprint"]
            )
            + len(sprint_report["contents"]["issuesCompletedInAnotherSprint"])
            + len(sprint_report["contents"]["puntedIssues"])
            - len(sprint_report["contents"]["issueKeysAddedDuringSprint"]),
            sum(
                float(sprint_report["contents"].get(key, {}).get("value", 0))
                for key in [
                    "completedIssuesInitialEstimateSum",
                    "issuesNotCompletedInitialEstimateSum",
                    "puntedIssuesInitialEstimateSum",
                    "issuesCompletedInAnotherSprintInitialEstimateSum",
                ]
            ),
        ]

    return removed, done, completed_outside, in_progress, to_do, total_committed

def calculate_sprint_details(
    board_config,
    sprint_report,
    on_start: Callable[[float, str], None] = None,
    on_iteration: Callable[[str], None] = None,
    on_finish: Callable[[str], None] = None,
) -> dict[str, str]:

    if on_start is None:

        def on_start(_x, _y):
            pass

    if on_iteration is None:

        def on_iteration(_y):
            pass

    if on_finish is None:

        def on_finish(_x):
            pass

    start = datetime.strptime(
        sprint_report["sprint"]["isoStartDate"], "%Y-%m-%dT%H:%M:%S%z"
    ).date()

    end = datetime.strptime(
        sprint_report["sprint"]["isoEndDate"], "%Y-%m-%dT%H:%M:%S%z"
    ).date()

    weekmask = " ".join(
        [
            k.capitalize()[:3]
            for k, v in dict(board_config["workingDaysConfig"]["weekDays"]).items()
            if v is True
        ]
    )
    holidays = [
        datetime.strptime(date, "%Y-%m-%d").date()
        for date in [
            x["iso8601Date"]
            for x in board_config["workingDaysConfig"]["nonWorkingDays"]
        ]
    ]

    days = np.busday_count(start, end, holidays=holidays, weekmask=weekmask)

    if days > 1:
        days = days + 1  # include the start day

    return {
        "name": str(sprint_report["sprint"]["name"]),
        "goal": str(sprint_report["sprint"]["goal"]),
        "start_date_string": str(sprint_report["sprint"]["startDate"]),
        "start_date": start,
        "end_date_string": str(sprint_report["sprint"]["endDate"]),
        "duration_days": str(days),
    }

def load_committed_vs_planned_chart(removed: DataPoint, done: DataPoint, completed_outside: DataPoint, in_progress: DataPoint, to_do: DataPoint, total_committed: tuple[int, int]) -> str:
    data_points = [
        removed,
        done,
        completed_outside,
        in_progress,
        to_do,
    ]
    colors = [dp.color for dp in data_points]
    hatches = [dp.hatch for dp in data_points]
    edge_colors = [dp.edge_color for dp in data_points]
    _, ax1 = plt.subplots()
    bottom = 0
    bars1 = []

    for i, data_point in enumerate(data_points):
        bars1.append(
            ax1.bar(
                "Issues",
                data_point.count,
                bottom=bottom,
                color=colors[i],
                width=0.4,
                edgecolor=edge_colors[i],
                hatch=hatches[i],
                align="center",
            )
        )
        bottom += data_point.count if data_point.count > 0 else 0

    ax1.set_ylabel("# Issues")
    ax1.vlines(
        x=-0.3,
        ymin=0,
        ymax=total_committed[0],
        color="#8590a2",
        linestyle="solid",
        linewidth=5,
    )

    ax2 = ax1.twinx()
    bottom = 0
    bars2 = []

    for i, data_point in enumerate(data_points):
        bars2.append(
            ax2.bar(
                "Est",
                data_point.points,
                bottom=bottom,
                color=colors[i],
                width=0.4,
                edgecolor=edge_colors[i],
                hatch=hatches[i],
                align="center",
            )
        )
        bottom += data_point.points if data_point.points > 0 else 0

    ax2.set_ylabel("Estimation Stat")
    ax2.vlines(
        x=0.7,
        ymin=0,
        ymax=total_committed[1],
        color="#8590a2",
        linestyle="solid",
        linewidth=5,
    )
    # ax1.axhline(0, color="black", linewidth=0.8)
    ax1.set_ylim(
        data_points[0].count * 1.1,
        max(
            [
                total_committed[0],
                data_points[1].count
                + data_points[2].count
                + data_points[3].count
                + data_points[4].count,
            ]
        )
        * 1.1,
    )
    ax2.set_ylim(
        data_points[0].points * 1.1,
        max(
            [
                total_committed[1],
                data_points[1].points
                + data_points[2].points
                + data_points[3].points
                + data_points[4].points,
            ]
        )
        * 1.1,
    )
    y1mn, y1mx = ax1.get_ylim()
    y1ticks = ax1.get_yticks()
    y2mn, y2mx = ax2.get_ylim()
    y2ticks = ax2.get_yticks()

    if y1mn * y1mx > 0:
        raise ValueError("y1mn * y1mx > 0")
    if y2mn * y2mx > 0:
        raise ValueError("y2mn * y2mx > 0")

    d1 = y1mx - y1mn
    d2 = y2mx - y2mn
    r1 = -y1mx / y1mn if y1mn != 0 else 0
    r2 = -y2mx / y2mn if y2mn != 0 else 0

    if d1 > d2:
        if r1 > r2:
            y2mx = -y2mn * r1 if y2mn != 0 else y2mx
        else:
            y2mn = -y2mx / r1 if r1 != 0 else y2mn
    else:
        if r2 > r1:
            y1mx = -y1mn * r2 if y1mn != 0 else y1mx
        else:
            y1mn = -y1mx / r2 if r2 != 0 else y1mn

    ax1.set_ylim(y1mn, y1mx)
    ax1.set_yticks(y1ticks)
    ax2.set_ylim(y2mn, y2mx)
    ax2.set_yticks(y2ticks)

    # Add labels to each bar in the first set of bars
    for chart_bar in bars1:
        for rect in chart_bar:
            height = rect.get_height()
            if height != 0:  # Avoid labeling bars with height of zero
                ax1.text(
                    rect.get_x() + rect.get_width() / 2.0,
                    rect.get_y() + height / 2.0,
                    f"{height}",
                    ha="center",
                    va="center",
                )

    # Add labels to each bar in the second set of bars
    for chart_bar in bars2:
        for rect in chart_bar:
            height = rect.get_height()
            if height != 0:  # Avoid labeling bars with height of zero
                ax2.text(
                    rect.get_x() + rect.get_width() / 2.0,
                    rect.get_y() + height / 2.0,
                    f"{height}",
                    ha="center",
                    va="center",
                )

    if total_committed[0] > 0:
        ax1.text(
            -0.3,
            total_committed[0] + 0.4,
            f"{str(total_committed[0]).rjust(3)}",
            color="black",
            horizontalalignment="center",
            fontweight="bold",
        )

    if total_committed[1] > 0:
        ax2.text(
            0.7,
            total_committed[1] + 0.4,
            f"{str(total_committed[1]).rjust(3)}",
            color="black",
            horizontalalignment="center",
            fontweight="bold",
        )

    legend_elements = [
        Line2D([0], [0], color="#8590a2", lw=2, label="Committed"),
        to_do.get_patch(),
        in_progress.get_patch(),
        done.get_patch(),
        completed_outside.get_patch(),
        removed.get_patch(),
    ]

    ax1.legend(handles=legend_elements, bbox_to_anchor=(1.15, 1), loc="upper left")
    plt.title("Committed vs Completed Chart")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", pad_inches=0.5)

    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()

    return image_base64
