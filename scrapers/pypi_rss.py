import json
import os
import xml.etree.ElementTree

import arrow
import requests

from cloudant_wrapper import add_date_view, get_cloudant_database
from utils import retry_get_tree, slugify, update_data


CONF = {'topic': 'python', 'source': 'pypi_rss', 'doc_type': 'feeds'}


def get_posts():
    url = 'https://pypi.python.org/pypi?%3Aaction=packages_rss'

    response = requests.get(url)

    if hasattr(response.content, 'decode'):
        tree = xml.etree.ElementTree.fromstring(response.content.decode('utf8'))
    else:
        tree = xml.etree.ElementTree.fromstring(response.content)

    channel = tree.find('channel')
    items = channel.findall('item')

    trending_posts = []
    for item in items:
        i_dict = {'_id': slugify(item[0].text.split()[0]),
                  'name': item[0].text.split()[0],
                  'url': item[1].text,
                  'description': item[3].text or '',
                  'date': str(arrow.get(item[4].text.split(' GMT')[0], 'DD MMM YYYY HH:mm:ss')),
                  'likes': []}
        trending_posts.append(i_dict)

    return trending_posts


def update():
    update_data(CONF, get_posts())

if __name__ == '__main__':
    update()
