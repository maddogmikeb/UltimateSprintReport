"""
Defines the `UltimateJiraSprintReport` class, which provides functionality
for generating sprint reports from Jira data. It includes methods for
interacting with Jira, loading plugins, and utilizing various utility
functions for report generation.

Classes:
   - UltimateJiraSprintReport: Main class for generating Jira sprint reports.

"""

# pylint: disable=import-outside-toplevel, protected-access
# pylint: disable=import-error
# pylint: disable=too-few-public-methods

class UltimateJiraSprintReport:
    """
    Main class for generating Jira sprint reports. It provides methods for interacting with Jira,
    loading plugins, and utilizing utility functions for report generation.

    Attributes:
       jira (Jira): Instance of the Jira client for interacting with Jira.
       PluginFolder (str): Path to the folder containing plugins.
       MainModule (str): Name of the main module for plugins.
    """

    # Import Models
    from models.data_point import DataPoint

    # Import Services
    from services.jira_service import JiraService

    # Import Functions
    from functions.burndown import load_burndown as burndown

    def __init__(self, username: str, password: str, jira_scheme_url: str):
        self.jira_service = self.JiraService(username, password, jira_scheme_url)
        self.jira_service.authenticate()

    def load_burndown(self, rapid_view_id: int, sprint_id: int):        
        self.burndown(
            self.jira_service,
            rapid_view_id,
            sprint_id,
        )

report = UltimateJiraSprintReport("username", "password", "url")
report.load_burndown(21, 123)