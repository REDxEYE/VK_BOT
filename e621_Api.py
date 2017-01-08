import json
import random
import urllib.request
from io import StringIO
from json import loads
from urllib.request import urlopen
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup


def e621(tags, n, page, sort_=None):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    url = 'http://e621.net/post/index/{}/{}'.format(page, '%20'.join(tags))
    print(url)
    link = []
    rnd = []
    aa = {}
    req = urllib.request.Request(url, headers=hdr)
    e621 = urlopen(req).read()
    soup = BeautifulSoup(e621, 'html.parser')
    imgs = str(soup.find('script', {'id': 'blacklisted-images'})).split('\n')
    for img in imgs:
        img = img.replace("\t", '')
        img = img.replace(";", '')
        # print(img)
        if img.startswith('Post.register'):
            img = img.replace("Post.register", '')
            js = loads(img[1:len(img) - 1])
            if js['file_ext'] == 'jpg' or js['file_ext'] == 'png':
                link.append([js['file_url'], js])
    if sort_ == 'random':
        a = random.sample(link, len(link))
        for i in a[:n]:
            rnd.append(i[0])
        return rnd
    if sort_:

        for a in link:
            aa[a[0]] = a[1][sort_]
        # print(aa)
        ss = sorted(aa, key=aa.__getitem__)
        ss = ss[::-1]

        return ss[:n]


def e926(tags, n, page, sort_=None):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    url = 'http://e926.net/post/index/{}/{}'.format(page, '%20'.join(tags))
    print(url)
    link = []
    rnd = []
    aa = {}
    req = urllib.request.Request(url, headers=hdr)
    e621 = urlopen(req).read()
    soup = BeautifulSoup(e621, 'html.parser')
    imgs = str(soup.find('script', {'id': 'blacklisted-images'})).split('\n')

    for img in imgs:
        img = img.replace("\t", '')
        img = img.replace(";", '')
        if img.startswith('Post.register'):
            img = img.replace("Post.register", '')
            js = loads(img[1:len(img) - 1])
            # print(js['file_ext']!='jpg')

            if js['file_ext'] == 'jpg' or js['file_ext'] == 'png':
                link.append([js['file_url'], js])
    print('parsed')

    if sort_ == 'random':
        a = random.sample(link, len(link))
        for i in a[:n]:
            rnd.append(i[0])
        return rnd
    if sort_:

        for a in link:
            aa[a[0]] = a[1][sort_]
        # print(aa)
        ss = sorted(aa, key=aa.__getitem__)
        ss = ss[::-1]

        return ss[:n]






        # return link


def e926v2(tags, n, sort_=None):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    js = json.loads(requests.request('GET', 'http://e926.net/post/index.json?tags={}'.format(' '.join(tags))).text)

    aa = {}
    for post in js:

        try:
            if sort_:
                aa[post['file_url']] = int(post[sort_])


        except:
            continue

    ss = sorted(aa, key=aa.__getitem__)
    ss = ss[::-1]
    return ss[:n]


def e621v2(tags, n, sort_=None):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    js = json.loads(requests.request('GET', 'http://e621.net/post/index.json?tags={}'.format(' '.join(tags))).text)

    aa = {}
    for post in js:

        try:
            if sort_:
                aa[post['file_url']] = int(post[sort_])


        except:
            continue

    ss = sorted(aa, key=aa.__getitem__)
    ss = ss[::-1]
    print(ss)
    return ss[:n]
def get(tags, n, page, sort_):
    return e621v2(tags, n, sort_)


def getSafe(tags, n, page, sort_):
    return e926v2(tags, n, sort_)

# print(e926v2(['female', 'order:score', '-animated', 'fnaf', 'rating:q'],50,'score'))
