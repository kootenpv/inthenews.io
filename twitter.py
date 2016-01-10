
import datetime
import time

import arrow
import yaml

from utils import normalize, slugify, update_data


with open('conf.yaml') as f:
    CONF = yaml.load(f)

CONF.update({'source': 'twitter', 'doc_type': 'posts'})


def get_id_from_post_fn(post):
    return slugify(post['description'])


def process_item_fn(row, dones):
    desc = row.xpath(
        './/p[contains(@class, "tweet-text")]')[0].text_content().encode('utf8').strip()
    date = int(row.xpath('.//span/@data-time')[0])
    links = row.xpath('.//a')
    url = links[2].text_content() if len(links) > 2 else ''
    twitter_item = {'name': row.xpath('//span[@class="username"]//b')[0].text_content(),
                    'date': str(arrow.get(date)),
                    'description': desc.decode(),
                    'url': url}
    return twitter_item


def update():
    for handle in CONF['twitter_handles']:
        CONF['url'] = 'https://twitter.com/{}'.format(handle)
        update_data(CONF, '//li[contains(@class, "js-stream-item")]',
                    process_item_fn, get_id_from_post_fn)

if __name__ == "__main__":
    update()
