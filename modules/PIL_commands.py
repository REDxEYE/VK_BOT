import os
import traceback
import urllib
from urllib.request import urlopen

import sys

from DataTypes.attachments import attachment
from Module_manager_v2 import ModuleManager
from libs.PIL_module import Glitch, GlitchGif, MakeGlitchGifVSH, MakeGlitchGif
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

@ModuleManager.command(names=["глюк"], perm='photo.glitch2', desc="Глючная обработка",cost=10)
@ModuleManager.argument('sigma',5,'Сила смещений',False)
@ModuleManager.argument('iter',150,'Кол-во семплов',False)
@ModuleManager.argument('size',32,'Размер блока',False)
@ModuleManager.argument('color',True,'Двигать каждый цвет отдельно (True либо False)',False)
@ModuleManager.argument('rand',True,'Случайные размеры блока',False)
class Command_Glitch_(C_template):
    name = ["глюк"]
    access = ['all']
    desc = "Глючная обработка"
    perm = 'photo.glitch2'
    cost = 10

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        sigma = self.vars.sigma
        iter = self.vars.iter
        size = self.vars.size
        Glitch_ = self.vars.color
        random_ = self.vars.rand
        atts = data.attachments
        Topost = []
        for att in atts:
            try:

                photo = att.photo.GetHiRes
            except:
                return False
            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            Glitch(file=Tmp.path_, sigma=sigma, blockSize=size, iterations=iter, random_=random_, Glitch_=Glitch_)
            Tmp.cachefile(Tmp.path_)
            att = self.api.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.rem()
        args['message'] = ':D'
        args['attachment'] = Topost

        self.api.Replyqueue.put(args)
        return True

@ModuleManager.command(names=["глюкгиф"], perm='photo.glitchGif', desc="Глючная обработка гифки",cost=30)
@ModuleManager.argument('sigma',5,'Сила смещений',False)
@ModuleManager.argument('iter',150,'Кол-во семплов',False)
@ModuleManager.argument('size',32,'Размер блока',False)
@ModuleManager.argument('color',True,'Двигать каждый цвет отдельно (True либо False)',False)
@ModuleManager.argument('rand',True,'Случайные размеры блока',False)
@ModuleManager.argument('vsh',True,'Накладывать VSH эффект',False)
@ModuleManager.argument('len_',30,'Кол-во кадров',False)
class Command_GlitchGif_(C_template):
    name = ["глюкгиф"]
    access = ['admin', "editor", "moderator"]
    desc = "Глючная обработка гифки"
    perm = 'photo.glitchGif'
    cost = 20
    
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        sigma = self.vars.sigma
        iter = self.vars.iter
        size = self.vars.size
        Glitch_ = self.vars.color
        random_ = self.vars.rand
        vsh = self.vars.vsh
        len_ = self.vars.len_
        atts = data.attachments # type: list[attachment}
        Topost = []
        for att in atts:
            print(att)
            if att.type == attachment.types.doc:
                try:
                    gif = att.doc.url
                except:
                    return False
                req = urllib.request.Request(gif, headers=HDR)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'gif')
                file = GlitchGif(Tmp.path_, sigma=sigma, blockSize=size, iterations=iter, random_=random_,
                                 Glitch_=Glitch_)
                doc, t = self.api.UploadDocFromDisk(file)
                Tmp.rem()
                os.remove(file)
                Topost.append(doc)

            if att.type == attachment.types.photo:

                photo = atts[0].photo.GetHiRes
                req = urllib.request.Request(photo, headers=HDR)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg')
                file = MakeGlitchGif(image=Tmp.path_, len_=len_, sigma=sigma, blockSize=size, iterations=iter,
                                     random_=random_, Glitch_=Glitch_) if not vsh else MakeGlitchGifVSH(Tmp.path_,
                                                                                                        sigma=sigma,
                                                                                                        blockSize=size,
                                                                                                        iterations=iter,
                                                                                                        random_=random_,
                                                                                                        Glitch_=Glitch_)
                doc, t = self.api.UploadDocFromDisk(file)
                Tmp.cachefile(file)
                os.remove(file)
                Topost.append(doc)
                Tmp.rem()

        args['message'] = ':D'
        args['attachment'] = Topost

        self.api.Replyqueue.put(args)
        return True
