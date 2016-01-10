import json
import os
import xml.etree.ElementTree

import arrow
import requests

from cloudant_wrapper import add_date_view, get_cloudant_database
from utils import slugify


def update():
    database = get_cloudant_database('python', 'pypi_rss', 'feeds')

    add_date_view(database)

    doc_info = database.all_docs().get().json()['rows']
    done_slugged_infos = set([x['id'] for x in doc_info])
    rev_info = {x['id']: x['value']['rev'] for x in doc_info}

    ###
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
        i_dict = {'name': item[0].text.split()[0],
                  'url': item[1].text,
                  'description': item[3].text or '',
                  'date': str(arrow.get(item[4].text.split(' GMT')[0], 'DD MMM YYYY HH:mm:ss'))}
        trending_posts.append(i_dict)

    trending_posts = [x for x in trending_posts if x]

    for post in trending_posts:
        slugged_info = slugify(post['name'])
        post['_id'] = slugged_info
        if slugged_info in done_slugged_infos:
            post['_rev'] = rev_info[post['_id']]

    database.bulk_docs(*trending_posts)

if __name__ == '__main__':
    update()
