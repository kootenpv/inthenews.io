
import datetime
import re

import yaml

from utils import slugify, update_data


with open('conf.yaml') as f:
    CONF = yaml.load(f)

URL_TEMPLATE = 'http://stackoverflow.com/questions/tagged/{}?sort=featured&pageSize=100'

CONF = {'source': 'stackoverflow', 'doc_type': 'bounties',
        'url': URL_TEMPLATE.format(CONF['topic'])}


def process_item_fn(row, done_links):
    lnk = row.xpath('.//div[@class="summary"]/h3/a/@href')
    if not lnk:
        return
    lnk = str(lnk[0])
    row_link = lnk if lnk.startswith('http') else 'https://stackoverflow.com' + lnk
    link_id = re.findall('/([0-9]+)/', row_link)[0]
    if link_id in done_links:
        return False
    done_links.add(link_id)
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
    print(title)
    sohub_item = {'title': title,
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


def get_id_from_post_fn(post):
    return slugify(post['title'])


def update():
    xpath_row = '//div[contains(@id, "question-summary")]'
    update_data(CONF, xpath_row, process_item_fn, get_id_from_post_fn)

if __name__ == "__main__":
    update()
