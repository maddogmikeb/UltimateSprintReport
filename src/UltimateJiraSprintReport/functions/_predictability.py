# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments

from collections.abc import Callable

from ..utils._predictability_utils import calculate_predictability_score


def calculate_predictability(
    velocity_statistics,
    sprint_id,
    this_sprint_points_completed,
    this_sprint_points_committed,
    on_start: Callable[[float, str], None]=lambda _, __: "",  # pylint: disable=unused-argument
    on_iteration: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
    on_finish: Callable[[str], None]=lambda _: "",  # pylint: disable=unused-argument
):
    this_sprint_predictability = None
    predictability_data = []

    on_start(len(velocity_statistics["sprints"]), "Starting calculations")

    for sprint in sorted(velocity_statistics["sprints"], key=lambda i:-i["sequence"]):
        sprint_id_str = str(sprint["id"])
        on_iteration(f"Checking sprint id: {sprint_id_str}")
        estimated_points = velocity_statistics["velocityStatEntries"][sprint_id_str][
            "estimated"
        ].get("value", 0)
        completed_points = velocity_statistics["velocityStatEntries"][sprint_id_str][
            "completed"
        ].get("value", 0)
        predictability_score, stars = calculate_predictability_score(
            estimated_points, completed_points
        )
        sprint["predictability_score"] = predictability_score
        sprint["stars"] = stars
        if str(sprint_id) == sprint_id_str:
            this_sprint_predictability = {
                "predictability_score": predictability_score,
                "stars": stars,
            }
        predictability_data.append(
            {
                "name": sprint["name"],
                "estimated_points": estimated_points,
                "completed_points": completed_points,
                "predictability_score": predictability_score,
                "stars": stars,
            }
        )

    if not this_sprint_predictability:
        predictability_score, stars = calculate_predictability_score(
            this_sprint_points_committed, this_sprint_points_completed
        )
        this_sprint_predictability = {
            "predictability_score": predictability_score,
            "stars": stars + " (interim)",
        }

    on_finish("Calculated predictability")

    return this_sprint_predictability, predictability_data
