# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments

"""
This module provides utility functions for working with pandas DataFrames and formatting data.

Functions:
    - make_clickable: Converts a value into a clickable HTML link for a given base URL.
    - format_timestamp: Converts a timestamp in milliseconds to a pandas datetime object.
    - chart_to_base64_image: Converts a matplotlib plot to a Base64-encoded image.
"""

import base64
import io
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


def chart_to_base64_image(plt):
    """
    Converts a matplotlib plot to a Base64-encoded image.

    This function takes a matplotlib plot object, saves it as a PNG image in memory,
    and encodes it as a Base64 string. This is useful for embedding plots in HTML or
    other formats that support Base64-encoded images.

    Args:
        plt (matplotlib.pyplot): The matplotlib plot object to be converted.

    Returns:
        str: A Base64-encoded string representation of the plot image.
    """
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", pad_inches=0.5)

    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return image_base64
