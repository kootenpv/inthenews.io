import requests
import re    
import os

file_dir = os.path.dirname(os.path.realpath(__file__))

def update_pypi_names():
    html = requests.get('https://pypi.python.org/pypi/?').text
    with open(file_dir + '/pypi_packages.txt', 'w') as f:
        f.write('\n'.join(set([x.lower() for x in re.findall('<a href="/pypi/([^/]+)', html)])))

def get_pypi_names():
    with open(file_dir + '/pypi_packages.txt') as fin:
        return fin.read().split('\n')
