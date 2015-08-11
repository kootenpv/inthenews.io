import json
import requests
import lxml.html
import time
import arrow
import os

file_dir = os.path.dirname(os.path.realpath(__file__))

def update_data():
    with open(file_dir + '/data/twitterlog.txt') as fin:
        dones = set(fin.read().split('\n'))
    r = None
    for tag in ['PlanetPython', 'gvanrossum']:
        while r is None or r.status_code != 200:
            try:
                r = requests.get('https://twitter.com/{}'.format(tag)) 
            except:
                time.sleep(60) 
        tree = lxml.html.fromstring(r.content)
        rows = tree.xpath('//li[contains(@class, "js-stream-item")]')
        if not rows:
            continue
        processed = [process_item(row, dones, tag) for row in rows]
        with open(file_dir + '/data/twitterresult.jsonlist', 'a') as f: 
            f.write('\n' + '\n'.join([str(json.dumps(x)) for x in processed if x][::-1]))
        with open(file_dir + '/data/twitterlog.txt', 'w') as f: 
            f.write('\n'.join(dones)) 
        time.sleep(10)        
    
def process_item(row, dones, tag):
    desc = row.xpath('.//p[contains(@class, "tweet-text")]')[0].text_content().encode('utf8').strip()
    if desc in dones:
        return False
    dones.add(desc)
    date = int(row.xpath('.//span/@data-time')[0])
    links = row.xpath('.//a')
    url = links[2].text_content() if len(links) > 2 else ''
    twitter_item = {'name' : tag, 
                     'date' : str(arrow.get(date)), 
                     'description' : desc,
                     'url' : url.encode('utf8')}
    return twitter_item
    
    
if __name__ == "__main__":
    update_data()
