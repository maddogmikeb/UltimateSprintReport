# pylint: disable=protected-access, import-error
# pylint: disable=line-too-long, too-many-arguments
# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments

import base64
from collections.abc import Callable
from datetime import datetime
import io
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..services._jira_service import JiraService
from ..utils._pandas_utils import make_clickable


def _find_status_by_id(statuses, status_id: int):
    for status in statuses:
        if int(status["id"]) == int(status_id):
            return status
    return {"name": "Unknown"}


def load_burndown(
    jira_service: JiraService,
    rapid_view_id: int,
    sprint_id: int,
    on_start: Callable[[float, str], None]=lambda _, __: "", # pylint: disable=unused-argument
    on_iteration: Callable[[str], None]=lambda _: "", # pylint: disable=unused-argument
    on_finish: Callable[[str], None]=lambda _: "", # pylint: disable=unused-argument
) -> pd.DataFrame | str:

    scope = []
    already_done = set()

    statuses = jira_service.get_statuses()

    scope_change_burndown_chart = jira_service.get_scope_change_burndown_chart(
        rapid_view_id, sprint_id
    )

    sprint_start = scope_change_burndown_chart["startTime"]
    sprint_end = scope_change_burndown_chart["endTime"]
    complete_time = (
        scope_change_burndown_chart["completeTime"]
        if "completeTime" in scope_change_burndown_chart
        else None
    )
    now = (
        scope_change_burndown_chart["now"]
        if "now" in scope_change_burndown_chart
        else None
    )
    already_checked_for_resolution = set()
    on_start(
        len(scope_change_burndown_chart["changes"].items()) * 2
        +len(scope_change_burndown_chart["openCloseChanges"].items()),
        "Loading burndown chart",
    )

    for ts, change_list in scope_change_burndown_chart["changes"].items():
        on_iteration(
            "Loading issue details: " + change_list[0]["key"],
        )
        timestamp = int(ts)
        for change in change_list:
            on_iteration(
                "Loading issue details: " + change["key"],
            )
            if change["key"] in already_done:
                continue
            if (
                "column" in change
                and "done" in change["column"]
                and timestamp <= sprint_start
            ):
                already_done.add(change["key"])
            if change["key"] not in already_checked_for_resolution:
                issue = jira_service.get_issue(
                    key=change["key"], fields="resolutiondate"
                )
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

    for ts, change_list in sorted(
        scope_change_burndown_chart["changes"].items(), key=lambda x: x
    ):
        on_iteration(
            "Loading issue details: " + change_list[0]["key"],
        )
        timestamp = int(ts)

        for change in change_list:
            # Skip parent issues
            if (
                change["key"] in scope_change_burndown_chart["issueToParentKeys"]
                and scope_change_burndown_chart["issueToParentKeys"][change["key"]]
                is not None
            ):
                continue

            # Ignore issues that were already completed before the sprint had started
            if change["key"] in already_done:
                continue

            statistic = np.nan
            last_status = ""

            if timestamp <= sprint_start:
                statistic = (
                    change["statC"]["newValue"]
                    if "statC" in change and "newValue" in change["statC"]
                    else np.nan
                )
                if change["key"] in [x["key"] for x in scope]:
                    for _, item in enumerate(scope):
                        if item["key"] == change["key"]:
                            if np.isnan(item["statistic"]):
                                item["statistic"] = float(statistic)
                            elif not np.isnan(statistic):
                                item["statistic"] += float(statistic)
                else:
                    scope.append(
                        {
                            "timestamp": sprint_start,
                            "key": change["key"],
                            "eventType": "Sprint start",
                            "eventDetail": "",
                            "statistic": float(statistic),
                        }
                    )
            elif (complete_time and timestamp <= complete_time) or (
                now and timestamp <= now
            ):
                if change["key"] in [x["key"] for x in scope]:
                    statistic = 0
                    for _, item in enumerate(scope):
                        if item["key"] == change["key"]:
                            if np.isnan(item["statistic"]):
                                pass
                            else:
                                if float(item["statistic"]) == 0:
                                    statistic += 0
                                else:
                                    statistic += -1 * float(item["statistic"])
                            last_status = item["eventDetail"]
                if last_status == "Issue removed from sprint":
                    if "added" in change and change["added"] is True:
                        pass  # if being re-added to the sprint
                    else:
                        continue
                if "column" in change and "done" in change["column"]:
                    if not np.isnan(statistic) and statistic != 0:
                        statistic = -1 * abs(statistic)  # ensure it's burning down
                    scope.append(
                        {
                            "timestamp": timestamp,
                            "key": change["key"],
                            "eventType": "Burndown",
                            "eventDetail": "Issue completed",
                            "statistic": statistic,
                        }
                    )
                elif "added" in change and change["added"] is False:
                    if not np.isnan(statistic) and statistic != 0:
                        statistic = -1 * abs(statistic)  # ensure it's burning down
                    scope.append(
                        {
                            "timestamp": timestamp,
                            "key": change["key"],
                            "eventType": "Scope change",
                            "eventDetail": "Issue removed from sprint",
                            "statistic": statistic,
                        }
                    )
                elif "added" in change and change["added"] is True:
                    scope.append(
                        {
                            "timestamp": timestamp,
                            "key": change["key"],
                            "eventType": "Scope change",
                            "eventDetail": "Issue added to sprint",
                            "statistic": np.nan,
                        }
                    )
                elif "statC" in change and "newValue" in change["statC"]:
                    statistic = (
                        change["statC"]["newValue"]
                        if "statC" in change and "newValue" in change["statC"]
                        else np.nan
                    )
                    if statistic != 0 and not np.isnan(statistic):
                        if "oldValue" in change["statC"]:
                            old_value = change["statC"]["oldValue"]
                            scope.append(
                                {
                                    "timestamp": timestamp,
                                    "key": change["key"],
                                    "eventType": "Scope change",
                                    "eventDetail": f"Estimate change from {old_value} to {statistic}",
                                    "statistic": statistic - old_value,
                                }
                            )
                        else:
                            scope.append(
                                {
                                    "timestamp": timestamp,
                                    "key": change["key"],
                                    "eventType": "Scope change",
                                    "eventDetail": f"Estimate of {statistic} has been added",
                                    "statistic": statistic,
                                }
                            )
                elif (
                    "statC" in change
                    and "oldValue" in change["statC"]
                    and "newValue" not in change["statC"]
                ):
                    scope.append(
                        {
                            "timestamp": timestamp,
                            "key": change["key"],
                            "eventType": "Scope change",
                            "eventDetail": f"Estimate of {abs(statistic)} has been removed",
                            "statistic": statistic,
                        }
                    )
                elif (
                    "statC" in change
                    and change["statC"] == {}
                    and "column" in change
                    and "notDone" in change["column"]
                    and "newStatus" in change["column"]
                ):
                    new_status_id = _find_status_by_id(
                        statuses, change["column"]["newStatus"]
                    )["name"]
                    scope.append(
                        {
                            "timestamp": timestamp,
                            "key": change["key"],
                            "eventType": "Issue state change",
                            "eventDetail": f"Status changed to {new_status_id}",
                            "statistic": np.nan,
                        }
                    )
                elif (
                    "column" in change
                    and "notDone" in change["column"]
                    and "done" not in change["column"]
                ):
                    new_status_id = (
                        (
                            " to "
                            +_find_status_by_id(
                                statuses, change["column"]["newStatus"]
                            )["name"]
                        )
                        if "newStatus" in change["column"]
                        else ""
                    )
                    scope.append(
                        {
                            "timestamp": timestamp,
                            "key": change["key"],
                            "eventType": "Issue state change",
                            "eventDetail": f"Status changed{new_status_id}",
                            "statistic": np.nan,
                        }
                    )
                else:
                    scope.append(
                        {
                            "timestamp": timestamp,
                            "key": change["key"],
                            "eventType": "UNKNOWN",
                            "eventDetail": "UNKNOWN",
                            "statistic": statistic,
                        }
                    )

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

    if complete_time:
        by = scope_change_burndown_chart["lastUserWhoClosedHtml"]
        name = re.search(r">(.*?)<", by).group(1)
        scope.append(
            {
                "timestamp": complete_time,
                "key": "",
                "eventType": f"Sprint ended by {name}",
                "eventDetail": "",
                "statistic": np.nan,
            }
        )
    scope.append(
        {
            "timestamp": sprint_start + 0.1,
            "key": "",
            "eventType": "Sprint started",
            "eventDetail": "",
            "statistic": np.nan,
        }
    )
    if now and ((complete_time and now < complete_time) or not complete_time):
        scope.append(
            {
                "timestamp": now,
                "key": "",
                "eventType": "Current",
                "eventDetail": "",
                "statistic": np.nan,
            }
        )

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
    df["key"] = df["key"].apply(lambda x: make_clickable(x, jira_service.host))
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
    # add now line to chart if not completed and we are given the now timestamp
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

    on_finish(100)

    return (
        df,
        image_base64
    )
