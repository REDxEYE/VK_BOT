import urllib.request

from bs4 import BeautifulSoup


def search(text):
    url = 'https://www.youtube.com/results?search_query={}'.format('+'.join(text))
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
