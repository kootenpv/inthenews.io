import json
import requests
import xml.etree.ElementTree
import arrow

url = 'https://pypi.python.org/pypi?%3Aaction=packages_rss'

response = requests.get(url)


if hasattr(response.content, 'decode'):
    tree = xml.etree.ElementTree.fromstring(response.content.decode())
else:
    tree = xml.etree.ElementTree.fromstring(response.content)

channel = tree.find('channel')
items = channel.findall('item')

collection = []
for item in items:
    i_dict = {'name': item[0].text.split()[0],
              'url': item[1].text,
              'description': item[3].text or '',
              'date': str(arrow.get(item[4].text.split(' GMT')[0], 'DD MMM YYYY HH:mm:ss'))}
    collection.append(i_dict)

with open('/Users/pascal/GDrive/pytrending/pypiresult.jsonlist', 'a') as f:
    f.write('\n' + '\n'.join([json.dumps(item) for item in collection][::-1]))
