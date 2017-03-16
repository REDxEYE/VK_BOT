import json

import requests

HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def GetTags(image):
    urlKeyWords = 'https://services.microstock.pro/keywording/keywords'
    urlquality = 'https://services.microstock.pro/aesthetics/quality'
    # req = Request(url,data ="json=^%^7B^%^22url^%^22^%^3A^%^22https^%^3A^%^2F^%^2Fpp.userapi.com^%^2Fc628230^%^2Fv628230019^%^2F3ba42^%^2FWT21Z4VvOnk.jpg^%^22^%^7D",headers=HDR,method='POST' )
    print('Trying to get tags for ', image)
    KeyWords = requests.request('POST', urlKeyWords, data={'json': json.dumps({'url': image})}, headers=HDR).json()
    quality = requests.request('POST', urlquality, data={'json': json.dumps({'url': image})}, headers=HDR).json()
    return KeyWords['keywords']['keywords'], quality['quality']['score'] * 100


if __name__ == '__main__':
    print(GetTags('https://pp.userapi.com/c837632/v837632349/4fd28/g2_95FBp5Tk.jpg'))
