
import datetime

import yaml

from utils import retry_get_tree, slugify, update_data


with open('conf.yaml') as f:
    CONF = yaml.load(f)

URL_TEMPLATE = 'http://stackoverflow.com/questions/tagged/{}?sort=featured&pageSize=100'

CONF = {'source': 'stackoverflow', 'doc_type': 'bounties',
        'url': URL_TEMPLATE.format(CONF['stackoverflow'])}


def process_item_fn(row):
    lnk = row.xpath('.//div[@class="summary"]/h3/a/@href')
    if not lnk:
        return
    lnk = str(lnk[0])
    row_link = lnk if lnk.startswith('http') else 'https://stackoverflow.com' + lnk
    title = row.xpath('.//div[@class="summary"]/h3/a')[0].text
    user_details = row.xpath('.//div[@class="user-details"]/a/@href')[0].split('/')
    author, author_profile = user_details[1], user_details[2]
    author_src = str(row.xpath('.//div[contains(@class, "gravatar-wrapper-32")]/img/@src')[0])
    bounty = row.xpath('.//div[@class="bounty-indicator"]')[0].text[1:]
    date = str(row.xpath('.//span[@class = "relativetime"]/@title')[0])
    votes = row.xpath('.//span[contains(@class, "vote-count-post")]/strong')[0].text
    answers = row.xpath('.//div[@class="stats"]/div[contains(@class, "answered")]/strong')[0].text
    views = row.xpath('.//div[contains(@class, "views")]')[0].text
    desc = row.xpath(
        './/div[@class = "summary"]/div[@class = "excerpt"]')[0].text.replace('\r\n', ' ').replace('\n', ' ')
    tags = [x.split('/')[-1] for x in row.xpath('.//a[@class = "post-tag"]/@href')]
    sohub_item = {'_id': slugify(title),
                  'title': title,
                  'author': author,
                  'author_src': author_src,
                  'author_profile': author_profile,
                  'bounty': bounty,
                  'date': date,
                  'likes': [{'at': datetime.datetime.now().isoformat()[:19], 'n': votes}],
                  'views': views,
                  'answers': answers,
                  'description': desc,
                  'tags': tags,
                  'url': row_link}
    return sohub_item


def get_posts():
    tree = retry_get_tree(CONF['url'])
    rows = tree.xpath('//div[contains(@id, "question-summary")]')
    rows = [process_item_fn(row) for row in rows]
    return rows


def update():
    update_data(CONF, get_posts())

if __name__ == "__main__":
    update()
