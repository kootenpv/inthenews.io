# -*- coding: utf-8 -*-

import tornado.web
import tornado.autoreload
import tornado.httpserver
from tornado.ioloop import PeriodicCallback
from tornado.ioloop import IOLoop

import os
import json
import sys

from helper import get_pypi_names

import reddit
import github
import stackoverflow
import pypi_rss
import twitter

file_dir = os.path.dirname(os.path.realpath(__file__))

pypi = get_pypi_names()

data = {}

def update_local_file_database(): 
    with open(file_dir + '/data/gitresult.jsonlist') as f:
        github_items = [json.loads(x) for x in f.read().split('\n') if x][-20:][::-1]
        for item in github_items: 
            if item['name'].lower() in pypi:
                item['pypi'] = 'True'
    with open(file_dir + '/data/redditresult.jsonlist') as f:
        reddit_items = [json.loads(x) for x in f.read().split('\n') if x][-20:][::-1] 
    with open(file_dir + '/data/pypiresult.jsonlist') as f:
        pypi_items = [json.loads(x) for x in f.read().split('\n') if x][-20:][::-1]
    with open(file_dir + '/data/twitterresult.jsonlist') as f:
        twitter_items = [json.loads(x) for x in f.read().split('\n') if x][-20:][::-1]
    with open(file_dir + '/data/soresult.jsonlist') as f:
        so_items = [json.loads(x) for x in f.read().split('\n') if x][-20:][::-1]
    data['github'] = github_items
    data['so'] = so_items
    data['reddit'] = reddit_items
    data['pypi'] = pypi_items
    data['twitter'] = twitter_items      

class MainHandler(tornado.web.RequestHandler):
    def get(self): 
        self.render('index.html', github_items = data['github'], reddit_items = data['reddit'], 
                    so_items = data['so'], pypi_items = data['pypi'], twitter_items = data['twitter'])

class AboutHandler(tornado.web.RequestHandler): 
    def get(self): 
        self.render('about.html')
        
settings = {'template_path' : os.path.join(os.path.dirname(__file__), 'templates'),
            'static_path' : os.path.join(os.path.dirname(__file__), 'static')}

if __name__ == '__main__':
    # to run the server, type-in $ python tornad_server.py

    if not data:
        update_local_file_database()
        
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/about", AboutHandler),
    ], **settings)

    HOST = os.getenv('VCAP_APP_HOST', 'localhost')
    
    PORT = int(os.getenv('VCAP_APP_PORT', '8000'))
    
    http_server = tornado.httpserver.HTTPServer(application) 
    http_server.listen(PORT, HOST)

    ioloop = IOLoop().instance()

    scrape_mappings = {reddit.update_data : 50 * 60 * 1000, 
                       github.update_data : 60 * 60 * 1000, 
                       stackoverflow.update_data : 70000 * 60 * 1000,
                       pypi_rss.update_data : 20 * 60 * 1000, 
                       twitter.update_data : 40 * 60 * 1000}

    schedules = [PeriodicCallback(fn, period, io_loop = ioloop) for fn, period in scrape_mappings.items()] 

    sched = PeriodicCallback(update_local_file_database, 14.4 * 60 * 1000, io_loop = ioloop)
    sched.start()
    
    for schedule in schedules:
        schedule.start() 
    
    if 'production' not in sys.argv:
        for root, dirs, files in os.walk('.', topdown=False):
            for name in files:
                if '#' not in name and 'DS_S' not in name and 'flymake' not in name and 'pyc' not in name:
                    tornado.autoreload.watch(root+'/'+name)
        tornado.autoreload.start(ioloop)

    ioloop.start()
