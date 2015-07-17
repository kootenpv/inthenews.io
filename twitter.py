import json
import requests
import lxml.html
import time
import arrow

with open('/Users/pascal/GDrive/pytrending/twitterlog.txt', encoding = 'utf8') as fin:
    dones = set(fin.read().split('\n'))

def get_data():
    r = None
    while r is None or r.status_code != 200:
        try:
            r = requests.get('https://twitter.com/planetpython') 
        except:
            time.sleep(60)
    tree = lxml.html.fromstring(r.text)
    rows = tree.xpath('//li[contains(@class, "js-stream-item")]')
    if not rows:
        return
    processed = [process_item(row) for row in rows]
    with open('/Users/pascal/GDrive/pytrending/twitterresult.jsonlist', 'a') as f: 
        f.write('\n' + '\n'.join([str(json.dumps(x)) for x in processed if x][::-1]))
    with open('/Users/pascal/GDrive/pytrending/twitterlog.txt', 'w') as f: 
        f.write('\n'.join(dones)) 
    
def process_item(row):
    desc = str(row.xpath('.//p[contains(@class, "tweet-text")]')[0].text_content()).strip()
    if desc in dones:
        return False
    dones.add(desc)
    date = int(row.xpath('.//span/@data-time')[0])
    links = row.xpath('.//a')
    url = links[2].text_content() if len(links) > 1 else ''
    twitter_item = {'name' : 'PlanetPython', 
                     'date' : str(arrow.get(date)), 
                     'description' : desc,
                     'url' : str(url)}
    return twitter_item
    
    
get_data()
