# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments

"""
This module provides utility functions for working with pandas DataFrames and formatting data.

Functions:
    - make_clickable: Converts a value into a clickable HTML link for a given base URL.
    - format_timestamp: Converts a timestamp in milliseconds to a pandas datetime object.
"""

import pandas as pd

def make_clickable(val: any, base_url: str):
    """
    Converts a value into a clickable HTML link for a given base URL.

    Args:
        self: The calling object (not used in the function logic).
        val (str): The value to be converted into a clickable link.
        base_url (str): The base URL to be used for the link.

    Returns:
        str: An HTML string containing the clickable link, or the original value if empty.
    """
    if val == "":
        return val

    return f'<a target="_blank" href="{base_url}/browse/{val}">{val}</a>'

def format_timestamp(timestamp):
    """
    Converts a timestamp in milliseconds to a pandas datetime object.

    Args:
        self: The calling object (not used in the function logic).
        timestamp (int): The timestamp in milliseconds.

    Returns:
        pandas.Timestamp: A pandas datetime object representing the timestamp.
    """
    return pd.to_datetime(timestamp / 1000, unit="s")
