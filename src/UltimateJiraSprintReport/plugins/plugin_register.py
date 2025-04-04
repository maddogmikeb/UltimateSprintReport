# pylint: disable=import-outside-toplevel, protected-access
# pylint: disable=import-error, unused-import
# pylint: disable=too-few-public-methods, line-too-long
# pylint: disable=missing-function-docstring, invalid-name, missing-module-docstring, missing-class-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements

from UltimateJiraSprintReport.plugins.plugin import Plugin
from UltimateJiraSprintReport.plugins.zephyr_scale.zephyr_sprint_report_plugin import ZephyrSprintReportPlugin
from UltimateJiraSprintReport.services._jira_service import JiraService

plugins = {
    "zephyr_scale": ZephyrSprintReportPlugin,
}


def get_plugin(plugin_name: str, jira_service: JiraService, **kwargs) -> Plugin:
    # # Very hacky way of plugins but only for so works for now
    # # be great to make this based on file location
    instance = plugins[plugin_name].__new__(plugins[plugin_name], jira_service)
    instance.__init__(jira_service, **kwargs)  # pylint: disable=unnecessary-dunder-call

    return instance
