# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments, line-too-long

TEST_APP = "com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page"

def make_testcase_clickable(val: str, base_url: str, project: str):
    if len(val) == 0:
        return val

    return f'<a target="_blank" href="{base_url}/projects/{project}?selectedItem={TEST_APP}#!/v2/testCase/{val}">{val}</a>'

def make_testcycle_clickable(val: str, base_url: str, project: str):
    if len(val) == 0:
        return val

    return f'<a target="_blank" href="{base_url}/projects/{project}?selectedItem={TEST_APP}#!/v2/testCycle/{val}">{val}</a>'
