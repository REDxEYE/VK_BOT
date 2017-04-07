import os
import urllib
from urllib.request import urlopen

from libs.PIL_module import Wanted, JonTron, SayMax, textPlain
from libs.tempfile_ import TempFile

HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

try:
    from .__Command_template import *
except:
    from __Command_template import *


class Command_WantedFunk(C_template):
    name = ["wanted"]
    access = ["all"]
    desc = "Вставляет 2 фото внутрь фото с написью Разыскивается"
    perm = 'photo.wanted'
    cost = 5
    @staticmethod
    def execute(bot:Vk_bot2.Bot, data:LongPoolMessage,Updates:Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        atts = data.attachments
        # print(atts)
        Topost = []
        if len(atts) != 2:
            args['message'] = 'Нужно 2 фотографии'
            bot.Replyqueue.put(args)
            return False
        try:

            photo = atts[0].photo._getbiggest()
        except:
            return False
        try:
            photo1 = atts[1].photo._getbiggest()
        except:
            return False
        req = urllib.request.Request(photo, headers=HDR)
        req1 = urllib.request.Request(photo1, headers=HDR)
        img = urlopen(req).read()
        img1 = urlopen(req1).read()
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        Wanted(Tmp.path_, Tmp1.path_)
        att = bot.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.rem()
        Tmp1.rem()
        args['attachment'] = Topost
        bot.Replyqueue.put(args)


class Command_JonTronFunk(C_template):
    name = ["jontron"]
    access = ['all']
    desc = "Вставляет фото в фото с ДжонТроном"
    perm = 'photo.jontron'
    cost = 5
    @staticmethod
    def execute(bot:Vk_bot2.Bot, data:LongPoolMessage,Updates:Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        atts = data.attachments
        # print(atts)
        Topost = []

        try:

            photo = atts[0].photo._getbiggest()
            req = urllib.request.Request(photo, headers=HDR)

            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            Tmp.cachefile(Tmp.path_)
            JonTron(Tmp.path_)
            att = bot.UploadFromDisk(Tmp.path_)

            Tmp.rem()
        except:
            text = data.custom['text'] if 'text' in data.custom else 'Meh...'
            size = data.custom['size'] if 'size' in data.custom else 120
            font = data.custom['font'] if 'font' in data.custom else 'times.ttf'
            x = int(data.custom['x']) if 'x' in data.custom else 100
            y = int(data.custom['y']) if 'y' in data.custom else 150
            if text == None:
                return False
            _path = textPlain(text, size, font, x, y, 512, 512)
            JonTron(_path)

            att = bot.UploadFromDisk(_path)
            os.remove(_path)
            del _path
        Topost.append(att)
        args['attachment'] = Topost
        bot.Replyqueue.put(args)


class Command_SayMaxFunk(C_template):
    name = ["saymax"]
    access = ['all']
    desc = "Даёте подержать ваше фото Сойке"
    perm = 'photo.saymax'
    cost = 5
    @staticmethod
    def execute(bot:Vk_bot2.Bot, data:LongPoolMessage,Updates:Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        atts = data.attachments
        # print(atts)
        Topost = []

        try:

            photo = atts[0].photo._getbiggest()
            req = urllib.request.Request(photo, headers=HDR)

            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')

            SayMax(Tmp.path_)
            Tmp.cachefile(Tmp.path_)
            att = bot.UploadFromDisk(Tmp.path_)
            Tmp.rem()
        except:
            text = data.custom['text'] if 'text' in data.custom else 'кок'
            size = data.custom['size'] if 'size' in data.custom else 300
            font = data.custom['font'] if 'font' in data.custom else 'times.ttf'
            x = int(data.custom['x']) if 'x' in args else 250
            y = int(data.custom['y']) if 'y' in args else 200
            if text == None:
                return False
            _path = textPlain(text, size, font, x, y, 1280, 720)
            SayMax(_path)
            att = bot.UploadFromDisk(_path)
            os.remove(_path)
            del _path
        Topost.append(att)

        args['attachment'] = Topost
        bot.Replyqueue.put(args)
