# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long

"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template


def show_login_details(self):
    """
    Generates an HTML table displaying the currently logged-in user's details.

    Returns:
        str: HTML string containing the user's display name and avatar.
    """
    me = self.jira_service.myself()
    template = Template(
        """
        <table>
            <tr>
                <td>Currently logged in as:</td>
                <td>${display_name}</td>
                <td><img src='${avatar_url}' /></td>
            </tr>
        </table>
    """
    )
    return template.substitute(
        display_name=me["displayName"],
        avatar_url=me["avatarUrls"]["32x32"]
    )

