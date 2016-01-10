# - Change CSE to v2
# - Add date to query

import json
import time

import arrow
import requests
import tldextract
import yaml

from utils import slugify, update_data


with open('conf.yaml') as f:
    CONF = yaml.load(f)

CONF.update({'source': 'google_search', 'doc_type': 'posts'})

GDATE = '%a, %d %b %Y %H:%M:%S %z'


def extract_domain(url):
    tld = ".".join([x for x in tldextract.extract(url) if x])
    protocol = url.split('//', 1)[0]
    return protocol + '//' + tld


def query_google(q, topic='t', scoring='d'):
    """ query google, giving urls to test for injectableness """
    templ = 'http://ajax.googleapis.com/ajax/services/search/news?v=1.0&q={}&topic={}scoring={}'
    query_url = templ.format(q, topic, scoring)
    return json.loads(requests.get(query_url).text)['responseData']['results']


def get_results(row):
    return {'_id': slugify(row['titleNoFormatting']),
            'url': row['unescapedUrl'],
            'title': row['titleNoFormatting'],
            'img': row['image']['url'] if 'image' in row else '',
            'date': str(arrow.get(int(time.mktime(time.strptime(row['publishedDate'], GDATE))))),
            'description': row['content'],
            'domain': extract_domain(row['unescapedUrl']),
            'likes': []}


def get_posts():
    return [get_results(row) for row in query_google(CONF['google_query'])]


def update():
    update_data(CONF, get_posts())

if __name__ == '__main__':
    update()
