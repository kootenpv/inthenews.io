

import datetime

from utils import normalize, retry_get_tree, slugify, update_data


def process_item_fn(row, conf):
    links = row.xpath('.//a[contains(@class,"title")]')
    for link in links:
        try:
            votes = row.xpath('.//div[contains(@class, "score likes")]')[0].text_content().strip()
            row_link = link.attrib['href'] if link.attrib['href'].startswith(
                'http') else 'http://reddit.com' + link.attrib['href']
            if int(votes) < conf['reddit_minimum_votes']:
                return False
            comment_a = row.xpath('.//a[contains(text(), "comment")]')[0]
            comments = comment_a.text.split()[0]
            comments = '0' if 'comment' in comments else comments
            title = normalize(link.text_content())
            tagline = row.xpath('.//p[@class="tagline"]')[0].text_content().split('by')
            date = row.xpath('.//time/@datetime')[0]
            author = tagline[1].split()[0]
            return {'_id': slugify(title),
                    'title': title,
                    'author': author,
                    'likes': {'at': datetime.datetime.now().isoformat()[:19], 'n': int(votes)},
                    'comments': comments,
                    'date': date,
                    'url': row_link,
                    'description': '',
                    'comment_link': comment_a.attrib['href']}
        except ValueError as e:
            print('reddit error', e)
    return False


def get_posts(conf):
    rows = []
    for url in conf['urls']:
        tree = retry_get_tree(url)
        rows = tree.xpath('//div[@id="siteTable"]/div')
        rows.extend([process_item_fn(row, conf) for row in rows])
    return rows


def update(conf):
    conf.update({'source': 'reddit', 'doc_type': 'posts',
                 'urls': ['http://www.reddit.com/r/{}'.format(x)
                          for x in conf['reddit']]})

    update_data(conf, get_posts(conf))
