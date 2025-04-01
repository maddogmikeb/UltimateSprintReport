import pandas as pd 

def calculate_predictability_score(self, estimated_points, completed_points):
    if estimated_points == 0:
        return None, "-"
    predictability_score = abs(1 - (completed_points / estimated_points))
    stars = calculate_predictability_score_stars(predictability_score)
    return predictability_score, stars

def calculate_predictability_score_stars(self, predictability_score: float):
    if predictability_score <= 0.2:
        return "★★★★★"
    elif predictability_score <= 0.4:
        return "★★★★"
    elif predictability_score <= 0.6:
        return "★★★"
    elif predictability_score <= 0.8:
        return "★★"
    elif predictability_score <= 1.0:
        return "★"
    else:
        return "☆"

def make_clickable(self, val, base_url):
    if val != "":
        return f'<a target="_blank" href="{base_url}/browse/{val}">{val}</a>'
    else:
        return val

def make_testcase_clickable(self, val, base_url, project):
    if val != "":
        testapp = "com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/v2/testCase"
        return f'<a target="_blank" href="{base_url}/projects/{project}?selectedItem={testapp}/{val}">{val}</a>'
    else:
        return val

def format_timestamp(self, timestamp):
    return pd.to_datetime(timestamp / 1000, unit="s")