import requests
import re    

def update_pypi_names():
    html = requests.get('https://pypi.python.org/pypi/?').text
    with open('/Users/pascal/GDrive/pytrending/pypi_packages.txt', 'w') as f:
        f.write('\n'.join(set([x.lower() for x in re.findall('<a href="/pypi/([^/]+)', html)])))

def get_pypi_names():
    with open('/Users/pascal/GDrive/pytrending/pypi_packages.txt') as fin:
        return fin.read().split('\n')
