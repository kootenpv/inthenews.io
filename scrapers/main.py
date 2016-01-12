import google_query
import github_scraper
import pypi_rss
import reddit
import stackoverflow
import twitter

    scrape_mappings = {
        callback(reddit.update): 50 * MINUTE,
        callback(github_scraper.update): 0.5 * HOUR,
        callback(stackoverflow.update): 12 * HOUR,
        callback(pypi_rss.update): 20 * MINUTE,
        callback(twitter.update): 40 * MINUTE,
        callback(update_pm_names): 2 * HOUR,
        callback(google_query.update): 2 * HOUR
    }

    schedules = [InitialPeriodicCallback(fn, period, 20 * MINUTE, io_loop=ioloop)
                 for fn, period in scrape_mappings.items()]

    for schedule in schedules:
        schedule.start()
