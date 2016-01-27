import lxml.html
import re
import time

import lxml.etree
import requests

from es_wrapper import es, save_bulk


def retry_get_tree(url, max_retries=5):
    req = None
    tries = 0
    while req is None or req.status_code > 400 and tries < max_retries:
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            time.sleep(30)
        tries += 1
    try:
        tree = lxml.html.fromstring(req.text)
    except lxml.etree.ParserError:
        tree = lxml.html.fromstring(req.content.decode('latin1'))
    return tree


def slugify(value):
    return re.sub(r'[^\w\s-]', '', re.sub(r'[-\s]+', '-', value)).strip().lower()


def normalize(s):
    return re.sub(r'\s+', lambda x: '\n' if '\n' in x.group(0) else ' ', s).strip()


# def update_data(conf, rows, latest_date_sort=True):
#     trending_posts = [row for row in rows if row]
#     if not trending_posts:
#         return

#     conf['topic'], conf['source'], conf['doc_type']

#     database = get_cloudant_database()
#     doc_info = database.all_docs().get().json()['rows']
#     done_slugged_infos = set([x['id'] for x in doc_info])
#     rev_info = {x['id']: x['value']['rev'] for x in doc_info}

#     keys = []
#     for post in trending_posts:
#         if post['_id'] in done_slugged_infos:
#             post['_rev'] = rev_info[post['_id']]
#             keys.append(post['_id'])

#     if len(keys) < 50:
#         doc_query = '?include_docs=true&keys={}'.format(keys).replace("'", '"')
#         already_trending = database.all_docs().get(doc_query).json()['rows']

#         already_trending = {x['doc']['_id']: x['doc'] for x in already_trending}

#         for post in trending_posts:
#             if post['_id'] in keys:
#                 post['likes'] = already_trending[post['_id']]['likes'] + post['likes']
#                 if not latest_date_sort:
#                     post['date'] = already_trending[post['_id']]['date']

#     database.bulk_docs(*trending_posts)


def update_data(conf, rows):
    trending_posts = [row for row in rows if row]
    if not trending_posts:
        return

    save_bulk(es, conf['topic'], conf['source'] + "_" + conf['doc_type'],
              trending_posts)
