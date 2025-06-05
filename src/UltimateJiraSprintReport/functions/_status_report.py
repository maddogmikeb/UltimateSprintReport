# pylint: disable=missing-module-docstring, missing-function-docstring, line-too-long
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments

from collections.abc import Callable

import numpy as np
import pandas as pd

def load_sprint_status_table(
        base_url,
        sprint_report,
        on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
        on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
    ) -> pd.DataFrame:

    if not sprint_report or len(sprint_report) == 0:
        raise ValueError("Sprint Report not loaded")

    report = []

    for issue in sprint_report["contents"]["completedIssues"]:
        report.append({
            "Type" : "Completed Issues",
            "Key": "<a href='" + base_url + "/browse/" + issue["key"] +"'>" + issue["key"] + "</a>" + ("*" if issue["key"] in sprint_report["contents"]["issueKeysAddedDuringSprint"] else ""),
            "Summary": issue["summary"],
            "Issue Type": "<img style='height: 16px; width: 16px;' src='" + issue["typeUrl"] + "' title='" + issue["typeName"] + "' />",
            "Priority": "<img style='height: 16px; width: 16px;' src='" + issue["priorityUrl"] + "' title='" + issue["priorityName"] + " '/>" if "priorityName" in issue else "",            "Status": "<span style='background-color: var(--" + issue["status"]["statusCategory"]["colorName"] + ");'>" + issue["status"]["name"] + "</span>",            "Estimate": issue["estimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["estimateStatistic"] and 
                "value" in issue["estimateStatistic"]["statFieldValue"] else np.nan,
            "Original Estimate": issue["estimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["estimateStatistic"] and 
                "value" in issue["estimateStatistic"]["statFieldValue"] else np.nan,
            "Current Estimate": issue["currentEstimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["currentEstimateStatistic"] and 
                "value" in issue["currentEstimateStatistic"]["statFieldValue"] else np.nan
        })

    for issue in sprint_report["contents"]["issuesNotCompletedInCurrentSprint"]:
        report.append({
            "Type" : "Issues Not Completed",
            "Key": "<a href='" + base_url + "/browse/" + issue["key"] +"'>" + issue["key"] + "</a>" + ("*" if issue["key"] in sprint_report["contents"]["issueKeysAddedDuringSprint"] else ""),
            "Summary": issue["summary"],
            "Issue Type": "<img style='height: 16px; width: 16px;' src='" + issue["typeUrl"] + "' title='" + issue["typeName"] + "' />",
            "Priority": "<img style='height: 16px; width: 16px;' src='" + issue["priorityUrl"] + "' title='" + issue["priorityName"] + " '/>" if "priorityName" in issue else "",            "Status": "<span style='background-color: var(--" + issue["status"]["statusCategory"]["colorName"] + ");'>" + issue["status"]["name"] + "</span>",
            "Original Estimate": issue["estimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["estimateStatistic"] and 
                "value" in issue["estimateStatistic"]["statFieldValue"] else np.nan,
            "Current Estimate": issue["currentEstimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["currentEstimateStatistic"] and 
                "value" in issue["currentEstimateStatistic"]["statFieldValue"] else np.nan
        })

    for issue in sprint_report["contents"]["issuesCompletedInAnotherSprint"]:
        report.append({
            "Type" : "Issues completed outside of this sprint",
            "Key": "<a href='" + base_url + "/browse/" + issue["key"] +"'>" + issue["key"] + "</a>" + ("*" if issue["key"] in sprint_report["contents"]["issueKeysAddedDuringSprint"] else ""),
            "Summary": issue["summary"],
            "Issue Type": "<img style='height: 16px; width: 16px;' src='" + issue["typeUrl"] + "' title='" + issue["typeName"] + "' />",
            "Priority": "<img style='height: 16px; width: 16px;' src='" + issue["priorityUrl"] + "' title='" + issue["priorityName"] + " '/>" if "priorityName" in issue else "",
            "Status": "<span style='background-color: var(--" + issue["status"]["statusCategory"]["colorName"] + ");'>" + issue["status"]["name"] + "</span>",
            "Original Estimate": issue["estimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["estimateStatistic"] and 
                "value" in issue["estimateStatistic"]["statFieldValue"] else np.nan,
            "Current Estimate": issue["currentEstimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["currentEstimateStatistic"] and 
                "value" in issue["currentEstimateStatistic"]["statFieldValue"] else np.nan
        })

    for issue in sprint_report["contents"]["puntedIssues"]:
        report.append({
            "Type" : "Issues Removed From Sprint",
            "Key": "<a href='" + base_url + "/browse/" + issue["key"] +"'>" + issue["key"] + "</a>" + ("*" if issue["key"] in sprint_report["contents"]["issueKeysAddedDuringSprint"] else ""),
            "Summary": issue["summary"],
            "Issue Type": "<img style='height: 16px; width: 16px;' src='" + issue["typeUrl"] + "' title='" + issue["typeName"] + "' />",
            "Priority": "<img style='height: 16px; width: 16px;' src='" + issue["priorityUrl"] + "' title='" + issue["priorityName"] + " '/>" if "priorityName" in issue else "",
            "Status": "<span style='background-color: var(--" + issue["status"]["statusCategory"]["colorName"] + ");'>" + issue["status"]["name"] + "</span>",
            "Original Estimate": issue["estimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["estimateStatistic"] and 
                "value" in issue["estimateStatistic"]["statFieldValue"] else np.nan,
            "Current Estimate": issue["currentEstimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["currentEstimateStatistic"] and 
                "value" in issue["currentEstimateStatistic"]["statFieldValue"] else np.nan
        })

    df = pd.DataFrame(report)

    def create_estimate_column(row):
        original = str(row["Original Estimate"]) if pd.notna(row["Original Estimate"]) else "-"
        current = str(row["Current Estimate"]) if pd.notna(row["Current Estimate"]) else "-"
        return current if original == current else original + " → " + current

    df['Estimate'] = df.apply(create_estimate_column, axis=1)

    return df
