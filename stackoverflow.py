import json
import requests
import lxml.html
import re
import time
import os

file_dir = os.path.dirname(os.path.realpath(__file__))

def normalize(s): 
    return re.sub(r'\s+', lambda x: '\n' if '\n' in x.group(0) else ' ', s).strip()

def update_data():
    with open(file_dir + '/data/solog.txt') as fin:
        done_links = set(fin.read().split('\n'))
    r = None
    while r is None or r.status_code > 299:
        try:
            r = requests.get('http://stackoverflow.com/questions/tagged/python?sort=featured&pageSize=100') 
        except:
            time.sleep(60)
    tree = lxml.html.fromstring(r.text)
    rows = tree.xpath('//div[contains(@id, "question-summary")]')
    if not rows:
        return
    processed = [process_item(row, done_links) for row in rows]
    if not any(processed):
        return
    with open(file_dir + '/data/soresult.jsonlist', 'a') as f: 
        f.write('\n' + '\n'.join([json.dumps(x) for x in processed if x]))
    with open(file_dir + '/data/solog.txt', 'w') as f: 
        f.write('\n'.join(done_links)) 

def process_item(row, done_links):
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
    desc = row.xpath('.//div[@class = "summary"]/div[@class = "excerpt"]')[0].text.replace('\r\n', ' ').replace('\n', ' ')
    tags = [x.split('/')[-1] for x in row.xpath('.//a[@class = "post-tag"]/@href')]
    sohub_item = {'title' : title, 
                  'author' : author, 
                  'author_src' :author_src, 
                  'author_profile' : author_profile, 
                  'bounty' : bounty, 
                  'date' : date, 
                  'votes' : votes,
                  'views' : views, 
                  'answers' : answers,
                  'description' : desc,
                  'tags' : tags,
                  'url' : row_link} 
    return sohub_item 

if __name__ == "__main__":
    update_data()
    
