"""
This module provides utility functions for working with pandas DataFrames and formatting data.

Functions:
    - make_clickable: Converts a value into a clickable HTML link for a given base URL.
    - format_timestamp: Converts a timestamp in milliseconds to a pandas datetime object.
"""
# pylint: disable=unused-argument

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
    if val != "":
        return f'<a target="_blank" href="{base_url}/browse/{val}">{val}</a>'
    else:
        return val

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