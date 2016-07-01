import datetime
from html.parser import HTMLParser
from time import mktime

import feedparser
from bs4 import BeautifulSoup as BS


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
    soup = BS(I['summary_detail']['value'], "html.parser")
    img = soup.find_all('img')[0]['src']
    text = strip_tags(I['summary_detail']['value']).replace(I['title'], "")
    title = I['title']
    # print(I)
    print("Date: ", ConvertTime(I.published_parsed))
    print('Title:', title)
    print('Text:', text)
    print('Img: ', img)
    print('Link:', I['link'], '\n')
