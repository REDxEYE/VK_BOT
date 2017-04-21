import json
import re
from pprint import pprint





from PIL import Image
import requests
def replacePhoto(pid:str,photo,remixsid):

    vk = 'https://vk.com/al_photos.php'
    a = requests.get(vk, params={'act': 'edit_photo', 'al': 1, 'photo': pid}, cookies={'remixsid':remixsid})
    data = a.text

    aid = re.compile('cur\.pvMoveToAlbum\.val\((.*)\)').findall(data)[0]
    upl_url, hash_ = re.compile(f'upload_url":"(.*)",.+post.+\'{pid}.+\'(.*)\'\)').findall(data)[0]
    b = requests.post(upl_url.replace('\/', '/'), files={'photo': open(photo, 'rb')},
                      headers={'Filename': 'Filtered.jpg','Upload':'Submit Query'}).json()
    payload = {
        '_query': json.dumps(b),
        'act': 'save_desc',
        'aid': aid,
        'al': 1,
        'filter_num': 0,
        'hash': hash_,
        'photo': pid,
    }

    requests.get(vk, params=payload,cookies = {'remixsid':remixsid})

