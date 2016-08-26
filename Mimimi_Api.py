import urllib.request

from bs4 import BeautifulSoup


def mimimi():
    url = 'http://mimimi.ru/random'

    mi = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(mi, 'html.parser')
    a = soup.find_all('div', {'class': 'mi-image'})[0]
    link = a.find_all('img')[0].get('src')
    return link
