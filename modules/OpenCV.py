import os
import urllib
from urllib.request import urlopen

from Module_manager_v2 import ModuleManager
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

@ModuleManager.command(names=["wanted"], perm='photo.wanted', desc="Вставляет 2 фото внутрь фото с написью Разыскивается")
class Command_WantedFunk(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        atts = data.attachments
        # print(atts)
        Topost = []
        if len(atts) != 2:
            msg = 'Нужно 2 фотографии'
            data.send_back(msg, [], True)
            return False
        try:

            photo = atts[0].photo.GetHiRes
        except:
            return False
        try:
            photo1 = atts[1].photo.GetHiRes
        except:
            return False
        req = urllib.request.Request(photo, headers=HDR)
        req1 = urllib.request.Request(photo1, headers=HDR)
        img = urlopen(req).read()
        img1 = urlopen(req1).read()
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        Wanted(Tmp.path_, Tmp1.path_)
        att = self.api.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.rem()
        Tmp1.rem()

        data.send_back("", [att], True)

@ModuleManager.command(names=["jontron"], perm='photo.jontron', desc="Вставляет фото в фото с ДжонТроном")
@ModuleManager.argument('text','Meh...','Текст',False)
@ModuleManager.argument('size',120,'Размер шрифта',False)
@ModuleManager.argument('font','times.ttf','Шрифт',False)
@ModuleManager.argument('x',100,'Х координата',False)
@ModuleManager.argument('y',150,'Y координата',False)
class Command_JonTronFunk(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        atts = data.attachments
        # print(atts)
        Topost = []

        try:

            photo = atts[0].photo.GetHiRes
            req = urllib.request.Request(photo, headers=HDR)

            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            Tmp.cachefile(Tmp.path_)
            JonTron(Tmp.path_)
            att = self.api.UploadFromDisk(Tmp.path_)

            Tmp.rem()
        except:

            text = self.vars.text
            size = self.vars.size
            font = self.vars.font
            x = self.vars.x
            y = self.vars.y
            if text == None:
                return False
            _path = textPlain(text, size, font, x, y, 512, 512)
            JonTron(_path)

            att = self.api.UploadFromDisk(_path)
            os.remove(_path)
            del _path
        data.send_back("",[att], True)

@ModuleManager.command(names=["saymax"], perm='photo.saymax', desc="Даёте подержать ваше фото Сойке")
@ModuleManager.argument('text','кок','Текст',False)
@ModuleManager.argument('size',300,'Размер шрифта',False)
@ModuleManager.argument('font','times.ttf','Шрифт',False)
@ModuleManager.argument('x',250,'Х координата',False)
@ModuleManager.argument('y',200,'Y координата',False)
class Command_SayMaxFunk(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        atts = data.attachments
        # print(atts)


        try:

            photo = atts[0].photo.GetHiRes
            req = urllib.request.Request(photo, headers=HDR)

            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')

            SayMax(Tmp.path_)
            Tmp.cachefile(Tmp.path_)
            att = self.api.UploadFromDisk(Tmp.path_)
            Tmp.rem()
        except:
            text = self.vars.text
            size = self.vars.size
            font = self.vars.font
            x = self.vars.x
            y = self.vars.y
            if text == None:
                return False
            _path = textPlain(text, size, font, x, y, 1280, 720)
            SayMax(_path)
            att = self.api.UploadFromDisk(_path)
            os.remove(_path)
            del _path
            data.send_back('', [att], True)
