# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments

from collections.abc import Callable
import numpy as np

from ..services._jira_service import JiraService

def calculate_epic_statistics(
        jira_service: JiraService,
        board_config,
        sprint_report,
        on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
        on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
        on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
    ):

    epic_stats = []

    try:
        estimation_field = board_config["estimationStatisticConfig"][
            "currentEstimationStatistic"
        ]["id"].replace("field_", "", 1)
        epics_being_worked_on = []

        for issue in sprint_report["contents"]["completedIssues"]:
            if issue["typeName"] == "Epic":
                epics_being_worked_on.append(issue["key"])
            elif "epic" in issue:
                epics_being_worked_on.append(issue["epic"])

        on_start(len(list(set(epics_being_worked_on))), "Started Checking Epics")

        for epic_key in list(set(epics_being_worked_on)):
            on_iteration("Loading issue details: " + epic_key)
            try:
                epic = jira_service.get_issue(key=epic_key)
                issues_in_epic = jira_service.jql_query(
                    jql='issue in portfolioChildIssuesOf("' + epic_key + '")',
                    fields=",".join(["status", estimation_field]),
                )
                total_pts = 0
                total_cnt = 0
                done_pts = 0
                done_cnt = 0

                for issue in issues_in_epic["issues"]:
                    if issue["fields"][estimation_field]:
                        total_pts += issue["fields"][estimation_field]
                        if issue["fields"]["status"]["statusCategory"]["name"] == "Done":
                            done_pts += issue["fields"][estimation_field]
                    total_cnt += 1
                    if issue["fields"]["status"]["statusCategory"]["name"] == "Done":
                        done_cnt += 1

                completed_pts_perc = 0
                try:
                    completed_pts_perc = (done_pts / total_pts) * 100
                except: # pylint: disable=bare-except
                    completed_pts_perc = np.nan

                completed_cnt_perc = 0
                try:
                    completed_cnt_perc = (done_cnt / total_cnt) * 100
                except:  # pylint: disable=bare-except
                    completed_cnt_perc = np.nan

                epic_stats.append(
                    {
                        "parent_key": (
                            epic["fields"]["parent"]["key"]
                            if "parent" in epic["fields"] and "key" in epic["fields"]["parent"]
                            else None
                        ),
                        "parent_summary":(
                            epic["fields"]["parent"]["fields"]["summary"]
                            if ("parent" in epic["fields"] and "fields" in epic["fields"]["parent"]
                                and "summary" in epic["fields"]["parent"]["fields"])
                            else None
                        ),
                        "key": epic["key"],
                        "summary": epic["fields"]["summary"],
                        "status_category":(
                            epic["fields"]["status"]["statusCategory"]["name"]
                            if epic["fields"]["status"]["statusCategory"]
                            and "name" in epic["fields"]["status"]["statusCategory"]
                            else "To Do"
                        ),
                        "done_pts": done_pts,
                        "total_pts": total_pts,
                        "completed_pts_perc": completed_pts_perc,
                        "done_cnt": done_cnt,
                        "total_cnt": total_cnt,
                        "completed_cnt_perc": completed_cnt_perc,
                    }
                )
            except Exception as e: # pylint: disable=broad-exception-caught
                epic_stats.append(
                    {
                        "parent_key": None,
                        "parent_summary": "Error",
                        "key": epic_key,
                        "summary": repr(e),
                        "status_category": "Error",
                        "done_pts": None,
                        "total_pts": None,
                        "completed_pts_perc": None,
                        "done_cnt": None,
                        "total_cnt": None,
                        "completed_cnt_perc": None,
                    }
                )
    except: # pylint: disable=bare-except
        pass

    on_finish("Done checking epics")

    return epic_stats
