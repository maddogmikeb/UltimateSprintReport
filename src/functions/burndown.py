# pylint: disable=protected-access, import-error
# pylint: disable=line-too-long

import io
import base64
import re
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from services.jira_service import JiraService
from utils.pandas_utils import make_clickable


def load_burndown(self, jira_service: JiraService, rapid_view_id: int, sprint_id: int):
    """
    Main function to load the burndown chart and table.
    """
    scope_change_burndown_chart = jira_service.get_scope_change_burndown_chart(
        rapid_view_id, sprint_id
    )

    scope = []
    already_done = set()
    already_checked_for_resolution = set()

    sprint_start, sprint_end, complete_time, now = _extract_sprint_times(
        scope_change_burndown_chart
    )

    _process_changes(
        jira_service,
        scope_change_burndown_chart,
        already_done,
        already_checked_for_resolution,
        sprint_start,
    )

    _process_open_close_changes(
        scope_change_burndown_chart, scope, complete_time
    )

    df = _generate_burndown_table(scope)

    img = _generate_burndown_chart(
        df, sprint_start, sprint_end, complete_time, now
    )

    self.burndown_table = df
    self.burndown_chart = f'<img id="burndown_chart" class="popupable" src="data:image/png;base64,{img}" alt="Burndown Chart"/>'

    return self


def _extract_sprint_times(scope_change_burndown_chart):
    """
    Extracts sprint start, end, complete, and current times from the burndown chart data.
    """
    sprint_start = scope_change_burndown_chart["startTime"]
    sprint_end = scope_change_burndown_chart["endTime"]
    complete_time = scope_change_burndown_chart.get("completeTime", None)
    now = scope_change_burndown_chart.get("now", None)
    return sprint_start, sprint_end, complete_time, now


def _process_changes(
    jira_service: JiraService,
    scope_change_burndown_chart,
    already_done,
    already_checked_for_resolution,
    sprint_start,
):
    """
    Processes changes in the burndown chart data and updates the scope.
    """
    for ts, change_list in scope_change_burndown_chart["changes"].items():
        timestamp = int(ts)
        for change in change_list:
            _process_single_change(
                jira_service,
                change,
                already_done,
                already_checked_for_resolution,
                timestamp,
                sprint_start,
            )


def _process_single_change(
    jira_service: JiraService,
    change,
    already_done,
    already_checked_for_resolution,
    timestamp,
    sprint_start,
):
    """
    Processes a single change and updates the scope.
    """
    if change["key"] in already_done:
        return

    if "column" in change and "done" in change["column"] and timestamp <= sprint_start:
        already_done.add(change["key"])

    if change["key"] not in already_checked_for_resolution:
        issue = jira_service.get_issue(key=change["key"], fields="resolutiondate")
        already_checked_for_resolution.add(change["key"])
        if (
            issue
            and "fields" in issue
            and "resolutiondate" in issue["fields"]
            and issue["fields"]["resolutiondate"]
        ):
            resolution_epoch = (
                datetime.strptime(
                    issue["fields"]["resolutiondate"],
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                ).timestamp()
                * 1000
            )
            if resolution_epoch <= sprint_start:
                already_done.add(change["key"])


def _process_open_close_changes(scope_change_burndown_chart, scope, complete_time):
    """
    Processes open/close changes in the burndown chart data and updates the scope.
    """
    for ts, closures in scope_change_burndown_chart["openCloseChanges"].items():
        timestamp = int(ts)
        for closure in closures:
            if "operation" not in closure:
                continue
            operation = closure["operation"].lower()
            by = closure["userDisplayNameHtml"]
            name = re.search(r">(.*?)<", by).group(1)
            if timestamp == complete_time:
                operation = "ended"
                scope.append(
                    {
                        "timestamp": timestamp,
                        "key": "",
                        "eventType": f"Sprint ended by {name}",
                        "eventDetail": "",
                        "statistic": np.nan,
                    }
                )
            elif timestamp < complete_time:
                scope.append(
                    {
                        "timestamp": timestamp,
                        "key": "",
                        "eventType": f"Sprint {operation} by {name}",
                        "eventDetail": "",
                        "statistic": np.nan,
                    }
                )


def _generate_burndown_table(scope):
    """
    Generates the burndown table as a pandas DataFrame.
    """
    scope.sort(key=lambda x: (x["timestamp"], x["key"]))

    df = pd.DataFrame(scope)
    df["Inc."] = df.apply(
        lambda row: (
            row.statistic
            if row.statistic > 0 or (row.statistic == 0 and row.eventType != "Burndown")
            else ""
        ),
        axis=1,
    )
    df["Dec."] = df.apply(
        lambda row: (
            row.statistic
            if row.statistic < 0 or (row.statistic == 0 and row.eventType == "Burndown")
            else ""
        ),
        axis=1,
    )
    df["statistic_copy"] = df["statistic"]
    df.fillna({"statistic_copy": 0}, inplace=True)
    df["Remaining"] = df["statistic_copy"].cumsum()
    df = df.drop("statistic_copy", axis=1)
    df = df.drop("statistic", axis=1)
    df["date"] = pd.to_datetime(df["timestamp"] / 1000, unit="s")
    df["timestamp"] = df["timestamp"].astype("string").str.split(".").str[0]
    df["key"] = df["key"].map(make_clickable)
    df = df.rename(
        columns={
            "timestamp": "Timestamp",
            "date": "Date",
            "key": "Issue",
            "eventType": "Event Type",
            "eventDetail": "Event Detail",
        }
    )
    df = df[
        [
            "Timestamp",
            "Date",
            "Issue",
            "Event Type",
            "Event Detail",
            "Inc.",
            "Dec.",
            "Remaining",
        ]
    ]
    return df


def _generate_burndown_chart(df, sprint_start, sprint_end, complete_time, now):
    """
    Generates the burndown chart as a base64-encoded image.
    """
    filtered_df = df[df["Event Type"] != "Sprint start"]
    x = filtered_df["Date"]
    y = filtered_df["Remaining"]
    plt.step(x, y, label="Remaining", where="post")
    guideline_end_date = pd.Timestamp(sprint_end / 1000, unit="s")
    guideline_start_date = pd.Timestamp(sprint_start / 1000, unit="s")
    plt.plot(
        [guideline_start_date, guideline_end_date],
        [y.iloc[0], 0],
        "r--",
        label="Guideline",
    )
    plt.grid(axis="x", color="0.95")
    plt.xticks(rotation=45)
    plt.axhline(y=0, color="black", linestyle="-", linewidth=0.25)
    if now and ((complete_time and now < complete_time) or not complete_time):
        plt.axvline(
            x=pd.to_datetime(now / 1000, unit="s"),
            color="green",
            linestyle="--",
            linewidth=0.25,
            label="Now",
        )
    plt.legend()
    plt.title("Burndown Chart")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", pad_inches=0.5)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()

    return image_base64
