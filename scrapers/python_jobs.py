import feedparser


fp = feedparser.parse('https://www.python.org/jobs/feed/rss/')

fp.entries
