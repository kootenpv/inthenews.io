import requests
import json
import lxml.html
import re
import time
import os

file_dir = os.path.dirname(os.path.realpath(__file__))

def normalize(s): 
    return re.sub(r'\s+', lambda x: '\n' if '\n' in x.group(0) else ' ', s).strip()

def update_data():
    with open(file_dir + '/data/redditlog.txt') as fin:
        done_links = set([x for x in fin.read().split('\n') if x])
    r = None
    while r is None or r.status_code != 200:
        try:
            r  = requests.get('http://www.reddit.com/r/Python') 
        except: 
            time.sleep(60) 
    tree = lxml.html.fromstring(r.text)
    rows = tree.xpath('//div[@id="siteTable"]') 
    if not rows:
        return
    rows = rows[0].xpath('div')
    processed = [process_item(row, done_links) for row in rows]
    with open(file_dir + '/data/redditresult.jsonlist', 'a') as f:  
        f.write('\n' + '\n'.join(set([json.dumps(x) for x in sorted(processed, key = lambda x: x['date'] if x else '9999') if x])))
    with open(file_dir + '/data/redditlog.txt', 'w') as f: 
        f.write('\n'.join(done_links)) 
    
def process_item(row, done_links): 
    links = row.xpath('.//a[contains(@class,"title")]')
    for link in links: 
        try:
            votes = row.xpath('.//div[contains(@class, "score likes")]')[0].text_content().strip()
            row_link = link.attrib['href'] if link.attrib['href'].startswith('http') else 'http://reddit.com' + link.attrib['href']
            if row_link in done_links:
                return False
            if int(votes) < 30:
                return False
            done_links.add(row_link) 
            comment_a = row.xpath('.//a[contains(text(), "comment")]')[0]
            comments = comment_a.text.split()[0]
            comments = '0' if 'comment' in comments else comments
            title = normalize(link.text_content())
            tagline = row.xpath('.//p[@class="tagline"]')[0].text_content().split('by')
            date = row.xpath('.//time/@datetime')[0]
            author = tagline[1].split()[0]
            return {'title' : title, 
                    'author' : author, 
                    'votes' : votes, 
                    'comments' : comments, 
                    'date' : date, 
                    'url' : row_link, 
                    'description' : '',
                    'comment_link' : comment_a.attrib['href']} 
        except ValueError:
            pass    
    return False

if __name__ == "__main__":
    update_data()
    
