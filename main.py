# -*- coding: utf-8 -*-

# templates load config
# main load config
# conditionally load things from only if python load pypi
# reimplement being in the pypi as check

import datetime
import json
import os
import sys

import tornado.autoreload
import tornado.httpserver
import tornado.web
from package_manager import get_pm_names, update_pm_names
from tornado.ioloop import IOLoop, PeriodicCallback

import github_scraper
import google_query
import reddit
import pypi_rss
import stackoverflow
import twitter
from cloudant_wrapper import get_cloudant_database


MILLISECOND = 1
SECOND = MILLISECOND * 1000
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 365.25 / 12
YEAR = DAY * 365.25

import yaml

with open('conf.yaml') as f:
    CONF = yaml.load(f)


class ItemCache():

    def __init__(self):
        self.github_items = None
        self.github_sponsored_items = None
        self.reddit_items = None
        self.so_items = None
        self.twitter_items = None
        self.pypi_items = None
        self.google_items = None
        self.packages = set()

    def update_local_file_database(self):
        print('updating db')
        # with open(file_dir + '/data/gitresult_sponsored.jsonlist') as f:
        #     github_sponsored_items = [json.loads(x) for x in f.read().split('\n') if x][-20:][::-1]
        #     for item in github_sponsored_items:
        #         if item['name'].lower() in pypi:
        #             item['pypi'] = 'True'
        #         item['sponsored'] = True
        self.github_sponsored_items = []
        self.packages = get_pm_names()
        self.reddit_items = get_items(CONF['topic'], 'reddit', 'posts')
        self.github_items = get_items(CONF['topic'], 'github', 'repositories')
        for item in self.github_items:
            if item['name'].lower() in self.packages:
                item['is_package'] = True
        self.so_items = get_items(CONF['topic'], 'stackoverflow', 'bounties')
        self.pypi_items = get_items(CONF['topic'], 'pypi_rss', 'feeds')
        self.twitter_items = get_items(CONF['topic'], 'twitter', 'posts')
        self.google_items = get_items(CONF['topic'], 'google_search', 'posts')


class InitialPeriodicCallback(PeriodicCallback):

    def __init__(self, callback, callback_time, initial_wait, io_loop=None):
        super(InitialPeriodicCallback, self).__init__(callback, callback_time, io_loop)
        self.callback_time, self.initial_wait = initial_wait, self.callback_time
        self.initial_done = False

    def _schedule_next(self):
        if self._running:
            current_time = self.io_loop.time()
            while self._next_timeout <= current_time:
                self._next_timeout += self.callback_time / 1000.0
            self._timeout = self.io_loop.add_timeout(self._next_timeout, self._run)

        if not self.initial_done:
            self.callback_time, self.initial_wait = self.initial_wait, self.callback_time
            self.initial_done = True
            print("now loading data every", self.callback_time)

file_dir = os.path.dirname(os.path.realpath(__file__))


def get_items(language, source, doc_type):
    db = get_cloudant_database(language, source, doc_type)
    dates = db.design('dateview').view('viewdate').get().json()
    keys = dates['rows'] if dates else []
    keys = [(x['key'], x['id']) for x in keys]
    keys = sorted(keys, key=lambda x: x[0], reverse=True)[:20]
    doc_query = '?include_docs=true&keys={}'.format([x[1] for x in keys])
    docs = db.all_docs().get(doc_query.replace("'", '"')).json()
    return [doc['doc'] for doc in docs['rows']]


class MainHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ('GET', 'HEAD', 'POST')

    def initialize(self, item_cache):
        self._item_cache = item_cache

    def get(self):
        self.render('index.html',
                    github_items=self._item_cache.github_items,
                    reddit_items=self._item_cache.reddit_items,
                    so_items=self._item_cache.so_items,
                    pypi_items=self._item_cache.pypi_items,
                    twitter_items=self._item_cache.twitter_items,
                    github_sponsored_items=self._item_cache.github_sponsored_items,
                    google_items=self._item_cache.google_items,
                    topic=CONF['topic'])

    def head(self):
        return self.get()

# pylint: disable=W0223


class AboutHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('about.html')

settings = {'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'static_path': os.path.join(os.path.dirname(__file__), 'static')}


def callback(fn):
    print(fn)
    return fn

if __name__ == '__main__':

    item_cache = ItemCache()
    application = tornado.web.Application([
        (r"/", MainHandler, dict(item_cache=item_cache)),
        (r"/about", AboutHandler),
    ], **settings)

    HOST = os.getenv('VCAP_APP_HOST', 'localhost')

    PORT = int(os.getenv('VCAP_APP_PORT', '8123'))

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT, HOST)

    ioloop = IOLoop().instance()

    scrape_mappings = {
        callback(reddit.update): 50 * MINUTE,
        callback(github_scraper.update): 0.5 * HOUR,
        callback(stackoverflow.update): 12 * HOUR,
        callback(pypi_rss.update): 20 * MINUTE,
        callback(twitter.update): 40 * MINUTE,
        callback(update_pm_names): 2 * HOUR
    }

    schedules = [InitialPeriodicCallback(fn, period, 20 * MINUTE, io_loop=ioloop)
                 for fn, period in scrape_mappings.items()]

    sched = InitialPeriodicCallback(item_cache.update_local_file_database, 20 * MINUTE, 1 * SECOND,
                                    io_loop=ioloop)
    sched.start()

    for schedule in schedules:
        schedule.start()

    if 'production' not in sys.argv:
        for root, dirs, files in os.walk('.', topdown=False):
            for name in files:
                if '#' not in name and 'DS_S' not in name and 'flymake' not in name and 'pyc' not in name:
                    tornado.autoreload.watch(root + '/' + name)
        tornado.autoreload.start(ioloop)

    ioloop.start()
