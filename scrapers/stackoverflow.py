
import datetime

from utils import retry_get_tree, slugify, update_data


URL_TEMPLATE = 'http://stackoverflow.com/questions/tagged/{}?sort=featured&pageSize=100'


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
    date = str(row.xpath('.//span[@class = "relativetime"]/@title')[0][:10])
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
                  'likes': {'at': datetime.datetime.now().isoformat()[:19], 'n': int(votes)},
                  'views': views,
                  'answers': answers,
                  'description': desc,
                  'tags': tags,
                  'url': row_link}
    return sohub_item


def get_posts(conf):
    rows = []
    for url in conf['urls']:
        tree = retry_get_tree(url)
        rows = tree.xpath('//div[contains(@id, "question-summary")]')
        rows.extend([process_item_fn(row) for row in rows])
    return rows


def update(conf):
    conf.update({'source': 'stackoverflow', 'doc_type': 'bounties',
                 'urls': [URL_TEMPLATE.format(x) for x in conf['stackoverflow']]})

    update_data(conf, get_posts(conf))
