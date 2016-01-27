
from collections import Counter

import arrow

from utils import retry_get_tree, slugify, update_data


def process_item_fn(row):
    try:
        desc = row.xpath(
            './/p[contains(@class, "tweet-text")]')[0].text_content().encode('utf8').strip()
        date = int(row.xpath('.//span/@data-time')[0])
        url = row.xpath('.//a[contains(@href, "status/")]/@href')
        if not url:
            return False
        url = 'https://twitter.com' + url[-1]
        handle_counter = Counter([x.text_content() for x in row.xpath(
            '//span[@class="username js-action-profile-name"]//b')])
        name = handle_counter.most_common(1)[0][0] if handle_counter else ''
        likes = row.xpath('.//span[@class="ProfileTweet-actionCountForPresentation"]/text()')
        twitter_item = {'_id': slugify(desc.decode()),
                        'name': name,
                        'date': str(arrow.get(date)),
                        'description': desc.decode(),
                        'url': url,
                        'likes': likes[-1] if likes else 0}
        return twitter_item
    except:
        return False


def get_posts(conf):
    posts = []
    for handle in conf['twitter_handles']:
        print(handle)
        conf['url'] = 'https://twitter.com/{}'.format(handle)
        tree = retry_get_tree(conf['url'])
        rows = tree.xpath('//li[contains(@class, "js-stream-item")]')
        posts.extend([process_item_fn(row) for row in rows])
    return posts


def update(conf):
    conf.update({'source': 'twitter', 'doc_type': 'posts'})
    update_data(conf, get_posts(conf))
