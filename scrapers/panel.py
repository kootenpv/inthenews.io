"""Start the scraping from here"""

import yaml

import github_scraper
import google_query
import pypi_rss
import reddit
import stackoverflow
import twitter


MILLISECOND = 1
SECOND = MILLISECOND * 1000
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 365.25 / 12
YEAR = DAY * 365.25

with open('../conf.yaml') as f:
    CONFIG = yaml.load(f)

scrape_mappings = {
    reddit.update: 50 * MINUTE,
    github_scraper.update: 0.5 * HOUR,
    stackoverflow.update: 12 * HOUR,
    pypi_rss.update: 20 * MINUTE,
    twitter.update: 40 * MINUTE,
    # update_pm_names: 2 * HOUR,
    google_query.update: 2 * HOUR
}

for sm in scrape_mappings:
    print(sm, scrape_mappings[sm])
    sm(CONFIG)
