TEST_APP = "com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page"

def make_testcase_clickable(self, val, base_url, project):
    if val == "":
        return val    
    return f'<a target="_blank" href="{base_url}/projects/{project}?selectedItem={TEST_APP}#!/v2/testCase/{val}">{val}</a>'
