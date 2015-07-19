import json
import requests
import lxml.html
import re
import time
import os

file_dir = os.path.dirname(os.path.realpath(__file__))

with open(file_dir + '/gitlog.txt') as fin:
    done_links = set(fin.read().split('\n'))

def normalize(s): 
    return re.sub(r'\s+', lambda x: '\n' if '\n' in x.group(0) else ' ', s).strip()

def get_data():
    r = None
    while r is None or r.status_code > 299:
        try:
            r = requests.get('https://github.com/trending?l=python') 
        except:
            time.sleep(60)
    tree = lxml.html.fromstring(r.text)
    rows = tree.xpath('//li[@class="repo-list-item"]')
    if not rows:
        return
    processed = [process_item(row) for row in rows]
    if not any(processed):
        return
    with open(file_dir + '/gitresult.jsonlist', 'a') as f: 
        f.write('\n' + '\n'.join([json.dumps(x) for x in processed if x]))
    with open(file_dir + '/gitlog.txt', 'w') as f: 
        f.write('\n'.join(done_links)) 

def get_repo_page(link):
    r = requests.get(link)
    tree = lxml.html.fromstring(r.text)
    stars = tree.xpath('//a[@class="social-count js-social-count"]')[0].text.strip().replace(',', '')
    desc = tree.xpath('//article//p')
    return {'stars' : stars , 
            'date' : tree.xpath('//div[@class="authorship"]//time/@datetime')[0],
            'description2' : desc[0].text_content() if desc else '' }
        
def process_item(row):
    lnk = row.xpath('h3/a')[0]
    row_link = lnk.attrib['href'] if lnk.attrib['href'].startswith('http') else 'https://github.com' + lnk.attrib['href']
    if row_link in done_links:
        return False
    print('new',row_link)
    done_links.add(row_link)
    res = normalize(row.text_content()).split('\n') 
    github_item = {'name' : res[3], 
                   'author' : res[1], 
                   'contributors' : [{'src' : k,  'name': v } for k,v in 
                                     zip(row.xpath('.//a/img/@src'), row.xpath('.//a/img/@title'))], 
                   'description' : res[4]}
    github_item.update(get_repo_page(row_link))
    return github_item 
    
get_data()
