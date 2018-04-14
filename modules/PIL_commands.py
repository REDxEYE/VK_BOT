import os
import traceback
import urllib
from urllib.request import urlopen

import sys
from PIL import Image,ImageOps
from DataTypes.attachments import attachment
from Module_manager_v2 import ModuleManager
from libs.PIL_module import Glitch, GlitchGif, MakeGlitchGifVSH, MakeGlitchGif
from libs.tempfile_ import TempFile
import ConsoleLogger

LOGGER = ConsoleLogger.ConsoleLogger('PIL_COMMANDS')
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
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
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

        data.send_back(":D", Topost, True)
        return True

import io
from PIL import Image,ImageChops,ImageOps,ImageEnhance
@ModuleManager.command(names=["глюкмаска"], perm='photo.glitch2', desc="Глючная обработка",cost=10)
@ModuleManager.argument('sigma',5,'Сила смещений',False)
@ModuleManager.argument('iter',150,'Кол-во семплов',False)
@ModuleManager.argument('size',32,'Размер блока',False)
@ModuleManager.argument('color',True,'Двигать каждый цвет отдельно (True либо False)',False)
@ModuleManager.argument('rand',True,'Случайные размеры блока',False)
class MaskGlitch(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        sigma = self.vars.sigma
        iter = self.vars.iter
        size = self.vars.size
        Glitch_ = self.vars.color
        random_ = self.vars.rand
        atts = data.attachments
        Topost = []
        if atts.__len__()<2:
            photo = atts[0].photo.GetHiRes
            mask = atts[0].photo.GetHiRes
        else:
            photo = atts[0].photo.GetHiRes
            mask = atts[1].photo.GetHiRes
        req = urllib.request.Request(photo, headers=HDR)
        reqMask = urllib.request.Request(mask, headers=HDR)
        img = urlopen(req).read()
        Mask_req = urlopen(reqMask).read()
        print(Mask_req)
        Mask_io = io.BytesIO()
        Orig_io = io.BytesIO()
        Mask_io.write(Mask_req)
        Orig_io.write(img)
        imgMask =Image.open(Mask_io) #type: Image
        imgOrig =Image.open(Orig_io) #type: Image
        imgMask = imgMask.resize(imgOrig.size)
        Tmp = TempFile(img, 'jpg')
        Glitch(file=Tmp.path_, sigma=sigma, blockSize=size, iterations=iter, random_=random_, Glitch_=Glitch_)

        imgGlitch = Image.open(open(Tmp.path_,'rb'))
        imgMask = ImageEnhance.Contrast(ImageOps.grayscale(imgMask))

        img = ImageChops.composite(imgOrig,imgGlitch,imgMask.enhance(1.3))
        a = open(Tmp.path_,'wb')
        img.save(a,'JPEG')

        Tmp.cachefile(Tmp.path_)
        att = self.api.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.rem()
        data.send_back(":D", Topost, True)
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
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
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

        data.send_back(":D", Topost, True)
        return True

@ModuleManager.command(names=["жыпег","шакал","сожми"], perm='photo.jpeg', desc="Шакал опять сжимает",cost=10)
@ModuleManager.argument('quality',50,'Сила жыпега',False,max_min=(1,100))

class Command_jpeg(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        def Jpeg(im, q):
            img = Image.open(im, 'r')
            LOGGER.debug('Q value',q)
            img.save(im,'JPEG',quality=q)

        LOGGER.debug('Шакал quality filled?', self.vars.is_filled('quality'))
        if self.vars.is_filled('quality'):
            quality = int(self.vars.quality)
        elif len(data.args)>=1:
            quality = int(data.args[0])
        else:
            quality = self.vars.quality

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
            Jpeg(Tmp.path_,quality)
            Tmp.cachefile(Tmp.path_)
            att = self.api.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.rem()
        data.send_back("Шакалище", Topost, True)
        return True