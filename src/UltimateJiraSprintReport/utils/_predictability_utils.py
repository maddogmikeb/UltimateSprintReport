"""
This module provides utility functions for calculating predictability scores and ratings.

Functions:
    - calculate_predictability_score: Calculates the predictability score and star rating.
    - calculate_predictability_score_stars: Converts a predictability score to a star rating.
"""


def calculate_predictability_score(estimated_points, completed_points):
    """
    Calculates the predictability score and its corresponding star rating.

    Args:
        self: The calling object (not used in the function logic).
        estimated_points (float): The total estimated points for the sprint.
        completed_points (float): The total completed points for the sprint.

    Returns:
        tuple: A tuple containing:
            - predictability_score (float or None): The calculated predictability score, 
                or None if estimated_points is 0.
            - stars (str): The star rating corresponding to the predictability score.
    """
    if estimated_points == 0:
        return None, "-"

    predictability_score = abs(1 - (completed_points / estimated_points))
    stars = calculate_predictability_score_stars(predictability_score)

    return predictability_score, stars


def calculate_predictability_score_stars(predictability_score: float):
    """
    Converts a predictability score into a star rating.

    Args:
        self: The calling object (not used in the function logic).
        predictability_score (float): The predictability score to be converted into a star rating.

    Returns:
        str: A string representing the star rating, ranging from "★★★★★" (best) to "☆" (worst).
    """
    if predictability_score <= 0.2:
        return "★★★★★"

    if predictability_score <= 0.4:
        return "★★★★"

    if predictability_score <= 0.6:
        return "★★★"

    if predictability_score <= 0.8:
        return "★★"

    if predictability_score <= 1.0:
        return "★"

    return "☆"
