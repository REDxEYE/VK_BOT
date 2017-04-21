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
class Command_Glitch_(C_template):
    name = ["глюк"]
    access = ['all']
    desc = "Глючная обработка"
    perm = 'photo.glitch2'
    cost = 10

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        sigma = int(data.custom['sigma']) if 'sigma' in data.custom else 5
        iter = int(data.custom['iter']) if 'iter' in data.custom else 150
        size = int(data.custom['size']) if 'size' in data.custom else 32
        Glitch_ = bool(data.custom['color']) if 'color' in data.custom else True
        random_ = bool(data.custom['rand']) if 'rand' in data.custom else True
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
class Command_GlitchGif_(C_template):
    name = ["глюкгиф"]
    access = ['admin', "editor", "moderator"]
    desc = "Глючная обработка гифки"
    perm = 'photo.glitchGif'
    cost = 20
    
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        sigma = int(data.custom['sigma']) if 'sigma' in data.custom else 5
        iter = int(data.custom['iter']) if 'iter' in data.custom else 150
        size = int(data.custom['size']) if 'size' in data.custom else 32
        vsh = bool(data.custom['vsh']) if 'vsh' in data.custom else False
        Glitch_ = bool(data.custom['color']) if 'color' in data.custom else True
        len_ = int(data.custom['len']) if 'len' in data.custom else 60
        random_ = bool(data.custom['rand']) if 'rand' in data.custom else True
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
