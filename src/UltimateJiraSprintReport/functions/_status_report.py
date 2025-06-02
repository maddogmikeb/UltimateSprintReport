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
            "Issue Type": "<span><img style='height: 16px; width: 16px;' src='" + issue["typeUrl"] + "'>" + issue["typeName"] + "</span>",
            "Priority": "<span><img  style='height: 16px; width: 16px;' src='" + issue["priorityUrl"] + "'>" + issue["priorityName"] + "</span>" if "priorityName" in issue else "",
            "Status": "<span style='background-color: var(--" + issue["status"]["statusCategory"]["colorName"] + ");'>" + issue["status"]["name"] + "</span>",            "Estimate": issue["estimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["estimateStatistic"] and 
                "value" in issue["estimateStatistic"]["statFieldValue"] else np.nan
        })

    for issue in sprint_report["contents"]["issuesNotCompletedInCurrentSprint"]:
        report.append({
            "Type" : "Issues Not Completed",
            "Key": "<a href='" + base_url + "/browse/" + issue["key"] +"'>" + issue["key"] + "</a>" + ("*" if issue["key"] in sprint_report["contents"]["issueKeysAddedDuringSprint"] else ""),
            "Summary": issue["summary"],
            "Issue Type": "<span><img style='height: 16px; width: 16px;' src='" + issue["typeUrl"] + "'>" + issue["typeName"] + "</span>",
            "Priority": "<span><img style='height: 16px; width: 16px;' src='" + issue["priorityUrl"] + "'>" + issue["priorityName"] + "</span>" if "priorityName" in issue else "",
            "Status": "<span style='background-color: var(--" + issue["status"]["statusCategory"]["colorName"] + ");'>" + issue["status"]["name"] + "</span>",
            "Estimate": issue["estimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["estimateStatistic"] and 
                "value" in issue["estimateStatistic"]["statFieldValue"] else np.nan
        })

    for issue in sprint_report["contents"]["issuesCompletedInAnotherSprint"]:
        report.append({
            "Type" : "Issues completed outside of this sprint",
            "Key": "<a href='" + base_url + "/browse/" + issue["key"] +"'>" + issue["key"] + "</a>" + ("*" if issue["key"] in sprint_report["contents"]["issueKeysAddedDuringSprint"] else ""),
            "Summary": issue["summary"],
            "Issue Type": "<span><img style='height: 16px; width: 16px;' src='" + issue["typeUrl"] + "'>" + issue["typeName"] + "</span>",
            "Priority": "<span><img style='height: 16px; width: 16px;' src='" + issue["priorityUrl"] + "'>" + issue["priorityName"] + "</span>" if "priorityName" in issue else "",
            "Status": "<span style='background-color: var(--" + issue["status"]["statusCategory"]["colorName"] + ");'>" + issue["status"]["name"] + "</span>",
            "Estimate": issue["estimateStatistic"]["statFieldValue"]["value"] if "estimateStatistic" in issue and 
                "statFieldValue" in issue["estimateStatistic"] and 
                "value" in issue["estimateStatistic"]["statFieldValue"] else np.nan
        })

    df = pd.DataFrame(report)
    df = df.fillna("-").infer_objects()

    return df
