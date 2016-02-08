
import datetime

from utils import normalize, retry_get_tree, slugify, update_data


URL_TEMPLATE = 'https://github.com/trending?l={}'


def get_repo_page(link):
    print(link, 1)
    tree = retry_get_tree(link)
    stars = tree.xpath(
        '//a[@class="social-count js-social-count"]')[0].text.strip().replace(',', '')
    desc = tree.xpath('//article//p')
    return {'likes': {'at': datetime.datetime.now().isoformat()[:19], 'n': int(stars)},
            'description2': desc[0].text_content() if desc else ''}


def process_item_fn(row):
    lnk = row.xpath('h3/a')[0]
    row_link = lnk.attrib['href'] if lnk.attrib['href'].startswith(
        'http') else 'https://github.com' + lnk.attrib['href']
    res = normalize(row.text_content()).split('\n')
    github_item = {'_id': slugify(res[1] + '-' + res[3]),
                   'name': res[3],
                   'author': res[1],
                   'date': datetime.datetime.now().isoformat()[:19],
                   'contributors': [{'src': k,  'name': v} for k, v in
                                    zip(row.xpath('.//a/img/@src'), row.xpath('.//a/img/@title'))],
                   'description': res[4],
                   'url': "https://github.com/{}/{}/".format(res[1], res[3])}
    github_item.update(get_repo_page(row_link))
    return github_item


def get_posts(conf):
    rows = []
    for url in conf['urls']:
        tree = retry_get_tree(url)
        rows = tree.xpath('//li[@class="repo-list-item"]')
        rows.extend([process_item_fn(row) for row in rows])
    return rows


def update(conf):
    conf.update({'source': 'github', 'doc_type': 'repositories',
                 'urls': [URL_TEMPLATE.format(x) for x in conf['github']]})

    update_data(conf, get_posts(conf))
