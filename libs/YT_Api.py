import urllib.request

from bs4 import BeautifulSoup
from httplib2 import iri2uri


def iri_to_uri(iri):
    """Transform a unicode iri into a ascii uri."""
    return bytes(iri2uri(iri))
def search(text):
    url = u'https://www.youtube.com/results?search_query={}'.format((u'+'.join(text)))
    url = iri2uri(url)
    print(url)
    yt = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(yt, 'html.parser')
    a = soup.find_all('div')
    links = []
    titles = []

    for i in a:

        if i.get("data-context-item-id"):

            video = i.h3.a
            link = video.get('href')
            title = video.get('title')
            if not link.startswith('/watch'):
                continue

            links.append("http://www.youtube.com" + link)
            titles.append(title)

    return links, titles

    # a = soup.find_all('a')
    # videos = []
    # for i in a:
    #    if i.get('href').startswith('/watch?v='):
    #        print(i.get('href'))
    # search('mlp')
