# pylint: disable=missing-module-docstring, missing-function-docstring

from collections.abc import Callable

from services.jira_service import JiraService


def calculate_epic_statistics(
    jira_service: JiraService,
    board_config,
    sprint_report,
    on_start: Callable[[float, str], None] = None,
    on_iteration: Callable[[str], None] = None,
    on_finish: Callable[[str], None] = None,
):

    if on_start is None:

        def on_start(_x, _y):
            pass

    if on_iteration is None:

        def on_iteration(_y):
            pass

    if on_finish is None:

        def on_finish(_x):
            pass

    epic_stats = []

    estimation_field = board_config["estimationStatisticConfig"][
        "currentEstimationStatistic"
    ]["id"].replace("field_", "", 1)
    epics_being_worked_on = []

    for issue in sprint_report["contents"]["completedIssues"]:
        if issue["typeName"] == "Epic":
            epics_being_worked_on.append(issue["key"])
        elif "epic" in issue:
            epics_being_worked_on.append(issue["epic"])

    for epic_key in list(set(epics_being_worked_on)):
        on_iteration("Loading issue details: " + epic_key)
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

        epic_stats.append(
            dict(
                parent_key=(
                    epic["fields"]["parent"]["key"]
                    if "parent" in epic["fields"] and epic["fields"]["parent"]
                    else None
                ),
                parent_summary=(
                    epic["fields"]["parent"]["fields"]["summary"]
                    if "parent" in epic["fields"] and epic["fields"]["parent"]
                    else None
                ),
                key=epic["key"],
                summary=epic["fields"]["summary"],
                status_category=(
                    epic["fields"]["status"]["statusCategory"]["name"]
                    if epic["fields"]["status"]["statusCategory"]
                    and "name" in epic["fields"]["status"]["statusCategory"]
                    else "To Do"
                ),
                done_pts=done_pts,
                total_pts=total_pts,
                completed_pts_perc=done_pts / total_pts * 100,
                done_cnt=done_cnt,
                total_cnt=total_cnt,
                completed_cnt_perc=done_cnt / total_cnt * 100,
            )
        )

    return epic_stats
