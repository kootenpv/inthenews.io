# -*- coding: utf-8 -*-

import tornado.web
import tornado.autoreload
import tornado

import os
import json
import arrow

from helper import get_pypi_names

pypi = get_pypi_names()

class MainHandler(tornado.web.RequestHandler):
    def get(self): 
        with open('/Users/pascal/GDrive/pytrending/gitresult.jsonlist') as f:
            github_items = list(reversed([json.loads(x) for x in f.read().split('\n') if x]))
            for item in github_items: 
                item['date'] = arrow.get(item['date']).humanize() if 'date' in item else '' 
                if item['name'].lower() in pypi:
                    item['pypi'] = 'True'
        with open('/Users/pascal/GDrive/pytrending/redditresult.jsonlist') as f:
            reddit_items = list(reversed([json.loads(x) for x in f.read().split('\n') if x])) 
            for item in reddit_items:
                item['date'] = arrow.get(item['date']).humanize() if 'date' in item else '' 
        with open('pypiresult.jsonlist') as f:
            pypi_items = list(reversed([json.loads(x) for x in f.read().split('\n') if x]))        
            for item in pypi_items:
                item['date'] = arrow.get(item['date']).humanize() if 'date' in item else '' 
        with open('twitterresult.jsonlist') as f:
            twitter_items = list(reversed([json.loads(x) for x in f.read().split('\n') if x]))
            for item in twitter_items:
                item['date'] = arrow.get(item['date']).humanize() if 'date' in item else '' 
        with open('/Users/pascal/GDrive/pytrending/soresult.jsonlist') as f:
            so_items = list(reversed([json.loads(x) for x in f.read().split('\n') if x])) 
            for item in so_items:
                item['date'] = arrow.get(item['date']).humanize() if 'date' in item else '' 
        self.render('index.html', github_items = github_items, reddit_items = reddit_items, 
                    so_items = so_items, pypi_items = pypi_items, twitter_items = twitter_items)

settings = {'template_path' : os.path.join(os.path.dirname(__file__), 'templates'),
            'static_path' : os.path.join(os.path.dirname(__file__), 'static')}

if __name__ == '__main__':
    # to run the server, type-in $ python tornad_server.py

    application = tornado.web.Application([
        (r"/", MainHandler),
    ], **settings)

    HOST = 'localhost'
    PORT = 8100
    application.listen(PORT, HOST)

    ioloop = tornado.ioloop.IOLoop().instance()
    
    if HOST == 'localhost': 
        for root, dirs, files in os.walk('.', topdown=False):
            for name in files:
                if '#' not in name and 'DS_S' not in name and 'flymake' not in name and 'pyc' not in name:
                    tornado.autoreload.watch(root+'/'+name)
        tornado.autoreload.start(ioloop)

    ioloop.start()
