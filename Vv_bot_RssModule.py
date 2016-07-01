import datetime
from time import mktime

import feedparser
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def ConvertTime(date):
    return datetime.datetime.fromtimestamp(mktime(date))


python_wiki_rss_url = "http://www.oszone.net/rss-cat-2.xml"
feed = feedparser.parse(python_wiki_rss_url)
for I in feed['entries'][:1]:
    print(I)
    print("Date: ", ConvertTime(I.published_parsed))
    print('Text:', strip_tags(I['summary_detail']['value']))
    print('Link:', I['link'], '\n')
