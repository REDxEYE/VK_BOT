import bs4
import iso8601
from requests import request


def GetUser(uid):
    url = 'https://vk.com/foaf.php?id={}'
    req = request('GET', url.format(uid))
    a = bs4.BeautifulSoup(req.text, "html.parser")
    b = a.find('ya:created')
    date = iso8601.parse_date(b.get('dc:date'))
    b = a.find('foaf:gender')
    Bdate = a.find('foaf:birthday')
    # print(a,type_ = 'FOAF DEBUG')
    out = {'reg': '{}.{}.{} в {}'.format(str(date.day), str(date.month), str(date.year), str(date.time())),
           'gender': b.text if b != None else 'Неизвестно', 'Bday': Bdate.text if Bdate != None else 'Неизвестно'}
    return out
