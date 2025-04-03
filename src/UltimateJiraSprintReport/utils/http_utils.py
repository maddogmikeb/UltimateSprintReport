import re

# pylint: disable=line-too-long
URL_REGEX = r"(https?)://([^/]+)/jira/software/c/projects/([^/]+)/boards/(\d+)/reports/sprint-retrospective\?sprint=(\d+)"

def parse_url(url):
    match = re.search(URL_REGEX, url)
    if not match:
        raise ValueError("Invalid URL: " + url)

    protocol = match.group(1)
    base_url = match.group(2)
    project = match.group(3)
    rapid_view_id = match.group(4)
    sprint_id = match.group(5)
    full_base_url = f"{protocol}://{base_url}"

    if (protocol is None or base_url is None or project is None or
        rapid_view_id is None or sprint_id is None):
        raise ValueError("Invalid URL: " + url)

    return full_base_url, project, rapid_view_id, sprint_id
