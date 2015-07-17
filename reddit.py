import requests
import json
import lxml.html
import re
import time

with open('/Users/pascal/GDrive/pytrending/redditlog.txt') as fin:
    done_links = set([x for x in fin.read().split('\n') if x])

def normalize(s): 
    return re.sub(r'\s+', lambda x: '\n' if '\n' in x.group(0) else ' ', s).strip()

def get_data():
    r = None
    while r is None or r.status_code != 200:
        try:
            r  = requests.get('http://www.reddit.com/r/Python') 
            print(r.status_code)
        except: 
            time.sleep(60) 
    tree = lxml.html.fromstring(r.text)
    rows = tree.xpath('//div[@id="siteTable"]') 
    if not rows:
        print('no rows')
        return
    rows = rows[0].xpath('div')
    processed = [process_item(row) for row in rows]
    with open('/Users/pascal/GDrive/pytrending/redditresult.jsonlist', 'a') as f: 
        f.write('\n' + '\n'.join([json.dumps(x) for x in processed if x]))
    with open('/Users/pascal/GDrive/pytrending/redditlog.txt', 'w') as f: 
        f.write('\n'.join(done_links)) 
    
def process_item(row): 
    links = row.xpath('.//a[contains(@class,"title")]')
    for link in links: 
        try:
            votes = row.xpath('.//div[contains(@class, "score likes")]')[0].text_content().strip()
            row_link = link.attrib['href'] if link.attrib['href'].startswith('http') else 'http://reddit.com' + link.attrib['href']
            if row_link in done_links:
                print(row_link, 'already done')
                return False
            if int(votes) < 30:
                print('not trending')
                return False
            done_links.add(row_link) 
            comments = row.xpath('.//a[contains(text(), "comment")]')[0].text.split()[0]
            comments = '0' if 'comment' in comments else comments
            title = normalize(link.text_content())
            tagline = row.xpath('.//p[@class="tagline"]')[0].text_content().split('by')
            date = row.xpath('.//time/@datetime')[0]
            author = tagline[1].split()[0]
            print('returning')
            return {'title' : title, 
                    'author' : author, 
                    'votes' : votes, 
                    'comments' : comments, 
                    'date' : date, 
                    'url' : row_link, 
                    'description' : ''} 
        except ValueError:
            pass    
    return False
    
get_data()
