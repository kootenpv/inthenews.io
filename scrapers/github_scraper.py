
import datetime

import yaml

from utils import normalize, retry_get_tree, slugify, update_data


with open('conf.yaml') as f:
    CONF = yaml.load(f)

CONF.update({'source': 'github', 'doc_type': 'repositories',
             'url': 'https://github.com/trending?l={}'.format(CONF['github'])})


def get_repo_page(link):
    print(link, 1)
    tree = retry_get_tree(link)
    stars = tree.xpath(
        '//a[@class="social-count js-social-count"]')[0].text.strip().replace(',', '')
    desc = tree.xpath('//article//p')
    return {'likes': [{'at': datetime.datetime.now().isoformat()[:19], 'n': stars}],
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
                   'description': res[4]}
    github_item.update(get_repo_page(row_link))
    return github_item


def get_posts():
    tree = retry_get_tree(CONF['url'])
    rows = tree.xpath('//li[@class="repo-list-item"]')
    rows = [process_item_fn(row) for row in rows]
    return rows


def update():
    update_data(CONF, get_posts(), latest_date_sort=False)

if __name__ == "__main__":
    update()
