import requests
from bs4 import BeautifulSoup


def search(text):
    url = 'http://www.deviantart.com/browse/all/?thumb_mode=0&section=&global=1&q={}'.format('+'.join(text))
    print(url)

    r1 = requests.get(url)
    DA = r1.content
    soup = BeautifulSoup(DA, "html.parser")
    # print(soup.prettify())
    links = soup.find_all('span', {'class': 'thumb'})
    Titles = []
    Links = []

    for link in links:

        if link.get('data-super-full-img'):
            # print(link.get('data-super-full-img'))
            Img_ = link.get('data-super-full-img')
            Span = link.find_all('span', {"class": "title"})
            Title = Span[0].text
            Titles.append(Title)
            # Links.append(Img[0].get('href'))
            Links.append(Img_)

    # (Titles)
    return Links, Titles


def user(name):
    url = 'http://{}.deviantart.com/gallery/?catpath=/'.format(name)
    print(url)
    Titles = []
    Links_ = []
    r1 = requests.get(url)
    DA = r1.content
    soup = BeautifulSoup(DA, "html.parser")

    if '404' in str(soup.title):
        print('404')
        return None, None
    # print(soup.prettify())
    Links = soup.find_all('a', {'class': 'thumb'})
    for Link in Links:
        try:
            if Link.get('data-super-full-img'):
                Title = Link.get('title')
                Link_ = Link.get('data-super-full-img')
                Titles.append(Title)
                Links_.append(Link_)
                # print(Title,Link_)
        except:
            continue
    return Links_, Titles
