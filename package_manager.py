import re
import requests


def get_pm_names():
    html = requests.get('https://pypi.python.org/pypi/?').text
    return set(re.findall('<a href="/pypi/([^/]+)', html))
