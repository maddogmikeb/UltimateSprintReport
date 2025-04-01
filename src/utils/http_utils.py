import re 

url_regex = r"(https?)://([^/]+)/jira/software/c/projects/([^/]+)/boards/(\d+)/reports/sprint-retrospective\?sprint=(\d+)"

def _parse_url(self, url):    
    match = re.search(url_regex, url)
    if not match:
        raise Exception("Invalid URL: " + url)
    
    protocol = match.group(1)
    base_url = match.group(2)
    project = match.group(3)
    rapidViewId = match.group(4)
    sprintId = match.group(5)
    full_base_url = f"{protocol}://{base_url}"
    if protocol == None or base_url == None or project == None or rapidViewId == None or sprintId == None:
        raise Exception("Invalid URL: " + url)
    return full_base_url, project, rapidViewId, sprintId
