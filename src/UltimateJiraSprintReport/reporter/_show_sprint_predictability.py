"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template


def show_sprint_predictability(self):
    """
    Generates an HTML section displaying the sprint predictability rating.

    Returns:
        str: HTML string containing the sprint predictability rating.
    """
    template = Template(
        """
        <h2>Rating: ${stars}</h2>
        """
    )

    if not self.this_sprint_predictability:
        return ""

    return template.substitute(stars=self.this_sprint_predictability["stars"])
