import lxml.html
import re
import time

import requests
from lxml.etree import ParserError

from cloudant_wrapper import add_date_view, get_cloudant_database


def retry_get_tree(url):
    req = None
    while req is None or req.status_code > 400:
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            time.sleep(30)

    try:
        tree = lxml.html.fromstring(req.text)
    except ParserError:
        tree = lxml.html.fromstring(req.content.decode('latin1'))
    return tree


def slugify(value):
    return re.sub(r'[^\w\s-]', '', re.sub(r'[-\s]+', '-', value)).strip().lower()


def normalize(s):
    return re.sub(r'\s+', lambda x: '\n' if '\n' in x.group(0) else ' ', s).strip()


def update_data(conf, xpath_row, process_item_fn, get_id_from_post_fn,
                latest_date_sort=True):
    database = get_cloudant_database(conf['topic'], conf['source'], conf['doc_type'])

    add_date_view(database)

    doc_info = database.all_docs().get().json()['rows']
    done_slugged_infos = set([x['id'] for x in doc_info])
    rev_info = {x['id']: x['value']['rev'] for x in doc_info}

    tree = retry_get_tree(conf['url'])

    rows = tree.xpath(xpath_row)
    if not rows:
        return
    trending_posts = [process_item_fn(row, done_slugged_infos) for row in rows]

    trending_posts = [x for x in trending_posts if x]
    keys = []
    for post in trending_posts:
        slugged_info = get_id_from_post_fn(post)
        post['_id'] = slugged_info
        if slugged_info in done_slugged_infos:
            post['_rev'] = rev_info[post['_id']]
            keys.append(post['_id'])

    doc_query = '?include_docs=true&keys={}'.format(keys).replace("'", '"')
    already_trending = database.all_docs().get(doc_query).json()['rows']

    already_trending = {x['doc']['_id']: x['doc'] for x in already_trending}

    for post in trending_posts:
        if post['_id'] in keys:
            post['likes'] = already_trending[post['_id']]['likes'] + post['likes']
            if not latest_date_sort:
                post['date'] = already_trending[post['_id']]['date']

    database.bulk_docs(*trending_posts)
