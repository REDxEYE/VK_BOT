import datetime
from html.parser import HTMLParser
from time import mktime

import feedparser
from bs4 import BeautifulSoup as BS


class RssParser:
    def __init__(self, url):
        self.url = url
        print('Rss bot loaded')

    class MLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.reset()
            self.fed = []

        def handle_data(self, d):
            self.fed.append(d)

        def get_data(self):
            return ''.join(self.fed)

    def strip_tags(self, html):
        s = self.MLStripper()
        s.feed(html)
        return s.get_data()

    def ConvertTime(self, date):
        return datetime.datetime.fromtimestamp(mktime(date))

    def Parse(self):
        rss = []
        url = 'http://' + self.url
        if 'www.' not in url:
            url.replace('http://', 'http://www.')
        # python_wiki_rss_url = "http://www.oszone.net/rss-cat-2.xml"
        feed = feedparser.parse('http://' + url)
        for I in feed['entries']:
            rssE = {}
            soup = BS(I['summary_detail']['value'], "html.parser")
            img = soup.find_all('img')[0]['src']
            text = self.strip_tags(I['summary_detail']['value']).replace(I['title'], "")
            title = I['title']
            # print(I)
            # print("Date: ", self.ConvertTime(I.published_parsed))
            rssE['date'] = self.ConvertTime(I.published_parsed)
            #print('Title:', title)
            rssE['title'] = title
            #print('Text:', text)
            rssE['text'] = text
            #print('Img: ', img)
            rssE['img'] = img
            #print('Link:', I['link'], '\n')
            rssE['ling'] = I['link']
            rss.append(rssE)

        return rss