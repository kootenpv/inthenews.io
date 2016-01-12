import re

import requests
import yaml

from cloudant_wrapper import get_cloudant_database


with open('conf.yaml') as f:
    CONF = yaml.load(f)


def update_pm_names():
    database = get_cloudant_database(CONF['topic'], 'pm', 'packages')
    html = requests.get('https://pypi.python.org/pypi/?').text
    packages = [{'_id': x.lower()} for x in re.findall('<a href="/pypi/([^/]+)', html)]
    database.bulk_docs(*packages)


def get_pm_names():
    database = get_cloudant_database(CONF['topic'], 'pm', 'packages')
    return set(x['id'] for x in database.all_docs().get().json()['rows'])
