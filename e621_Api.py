from json import loads
import random
from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup


def e621(tags, n):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    url = 'http://e621.net/post/index/1/{}'.format('%20'.join(tags))
    print(url)
    link = []
    rnd = []
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
            link.append(js['file_url'])
    for i in range(n):
        a = (random.choice(link))
        link.remove(a)
        rnd.append(a)

    return rnd


def e926(tags, n):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    url = 'http://e926.net/post/index/1/{}'.format('%20'.join(tags))
    print(url)
    link = []
    rnd = []
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
            link.append(js['file_url'])
    for i in range(n):
        a = (random.choice(link))
        link.remove(a)
        rnd.append(a)

    return rnd







    # return link


def get(tags, n):
    return e621(tags, n)


def getSafe(tags, n):
    return e926(tags, n)
