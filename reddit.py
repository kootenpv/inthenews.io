

import datetime

import yaml

from utils import normalize, retry_get_tree, slugify, update_data


with open('conf.yaml') as f:
    CONF = yaml.load(f)

CONF.update({'source': 'reddit', 'doc_type': 'posts',
             'url': 'http://www.reddit.com/r/{}'.format(CONF['reddit'])})


def process_item_fn(row):
    links = row.xpath('.//a[contains(@class,"title")]')
    for link in links:
        try:
            votes = row.xpath('.//div[contains(@class, "score likes")]')[0].text_content().strip()
            row_link = link.attrib['href'] if link.attrib['href'].startswith(
                'http') else 'http://reddit.com' + link.attrib['href']
            if int(votes) < 20:
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
                    'likes': [{'at': datetime.datetime.now().isoformat()[:19], 'n': votes}],
                    'comments': comments,
                    'date': date,
                    'url': row_link,
                    'description': '',
                    'comment_link': comment_a.attrib['href']}
        except ValueError as e:
            print('reddit error', e)
    return False


def get_posts():
    tree = retry_get_tree(CONF['url'])
    rows = tree.xpath('//div[@id="siteTable"]/div')
    rows = [process_item_fn(row) for row in rows]
    return rows


def update():
    update_data(CONF, get_posts())

if __name__ == "__main__":
    update()
