import os
import re
import traceback
import urllib
from time import sleep
from urllib.request import urlopen

import sys

import math

import ConsoleLogger
LOGGER = ConsoleLogger.ConsoleLogger('ImageEdits')
from DataTypes.attachments import attachment
from Module_manager_v2 import ModuleManager
from libs.photo_replacer import replacePhoto
from trigger import Trigger
from utils.StringBuilder import StringBuilder

try:

    from PIL import ImageGrab, Image

    windows = True
except ImportError:
    windows = False
    ImageGrab = None
No = False
Yes = True
from libs import e621_Api as e6, EveryPixel
from libs.GlitchLib import Merge
from libs.PIL_module import kok, kek, roll, rollsmast, add, resize_, Glitch2
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
except ImportError:
    from __Command_template import *
from utils import ArgBuilder


@ModuleManager.command(names=["кок"], perm='photo.kok', desc="Зеркалит картинку", cost=2)
class Command_Kok(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        try:
            att = data.attachments[0]
            if att.type == attachment.types.photo:
                photo = att.photo.GetHiRes
                req = urllib.request.Request(photo, headers=HDR)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg', NoCache=True)
                kok(Tmp.path_)
                att = self.api.UploadFromDisk(Tmp.path_)
                Tmp.cachefile(Tmp.path_)
                Tmp.rem()
                data.send_back("Кокать надо меньше", [att], True)
            return True
        except:
            return False


@ModuleManager.command(names=["кек"], perm='photo.kek', desc="Зеркалит картинку", cost=2)
class Command_Kek(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        try:
            att = data.attachments[0]
            if att.type == attachment.types.photo:
                photo = att.photo.GetHiRes
                req = urllib.request.Request(photo, headers=HDR)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg', NoCache=True)
                kek(Tmp.path_)
                att = self.api.UploadFromDisk(Tmp.path_)
                Tmp.cachefile(Tmp.path_)
                Tmp.rem()
                data.send_back("Кекать надо меньше", [att], True)
                return True
        except:
            return False


@ModuleManager.command(names=["обработай", 'фильтр'], perm='photo.filter', desc="Позволяет применять фильтры к фото",
                       cost=2)
class Command_Filter(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        try:
            att = data.attachments[0]
            if att.type == attachment.types.photo:
                photo = att.photo.GetHiRes
                req = urllib.request.Request(photo, headers=HDR)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg', NoCache=True)
                msg = 'Список фильтров:\n'
                FArr = dict(enumerate(self.api.MODULES.FILTERS))
                for filter_ in FArr:
                    Fname = self.api.MODULES.FILTERS[FArr[filter_]].desc
                    msg += "{}. {}\n".format(filter_ + 1, Fname)
                data.send_back(msg, [], True)

                t = Trigger(cond=lambda
                    Tdata: Tdata.user_id == data.user_id and Tdata.chat_id == data.chat_id and Tdata.body.isnumeric(),
                            callback=self.Render, Tmp=Tmp, bot=self.api, FArr=FArr)
                self.api.TRIGGERS.addTrigger(t)
                return True
        except Exception as Ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            TB = traceback.format_tb(exc_traceback)
            LOGGER.error(exc_type, exc_value, traceback.print_tb(exc_traceback))
            return False

    def Render(self, data: LongPoolHistoryMessage, result, Tmp, bot: Vk_bot2.Bot, FArr):
        if result == False:
            Tmp.rem()
            msg = "Время ожидания ответа истекло"
            data.send_back(msg, [], True)
            return
        ans = int(data.body) - 1
        filter_ = self.api.MODULES.FILTERS[FArr[ans]].funk
        LOGGER.info('used filter {}'.format(filter_.name))
        filter_().render(Tmp.path_)
        # print(args)
        Tmp.cachefile(Tmp.path_)
        data.send_back(filter_.name, [self.api.UploadFromDisk(Tmp.path_)], True)
        Tmp.rem()
        return


@ModuleManager.command(names=["увеличь"], perm='photo.resize', desc="Позволяет увеличивать\уменьшать фото")
@ModuleManager.argument('size', 1000, 'Желаемый размер, не более 3000', Yes)
class Command_Resize(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        x = self.vars.size
        Topost = []
        for att in data.attachments:
            try:
                photo = att.photo.GetHiRes
            except:
                return False
            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg', NoCache=True)
            msg = 'Поднимать резкость?\n Да\Нет'
            data.send_back(msg, [], True)
            t = Trigger(cond=lambda Tdata: Tdata.user_id == data.user_id and Tdata.chat_id == data.chat_id and (
                re.match(r"([Дд])а", Tdata.body) or re.match(r"([Нн])ет", Tdata.body)), callback=Command_Resize.resize,
                        Tmp=Tmp, args=args, x=x)
            self.api.TRIGGERS.addTrigger(t)

    def resize(self, data: LongPoolHistoryMessage, result, Tmp, args: ArgBuilder.Args_message, x):
        ans = data.body
        if result == False:
            Tmp.rem()
            args.message = "Время ожидания ответа истекло"
            self.api.Replyqueue.put(args)
        sharp = False
        if re.match(r'([Дд])а', ans):
            sharp = True
        elif re.match(r'([Нн])ет', ans):
            sharp = False
        resize_(x, Tmp.path_, sharp)
        msg = "Вотъ"
        att = [self.api.UploadFromDisk(Tmp.path_)]
        Tmp.cachefile(Tmp.path_)
        Tmp.rem()
        data.send_back(msg, [att], True)


from bs4 import *


@ModuleManager.command(names=["e621"], perm='core.e621', desc="Ищет пикчи на e612",
                       template="Ищет пикчи на e612, форма запроса:\n" \
                                "{botname}, e621\n" \
                                "tags:тэги через ;\n" \
                                "sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n" \
                                "n:кол-во артов(максимум 10)\n" \
                                "page:страница на которой искать")
@ModuleManager.argument('tags', '', 'Тэги через ";"', True)
@ModuleManager.argument('n', 5, 'Кол-во фото', No)

class Command_e621(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        tags = self.vars.tags.strip().split(';')
        n = self.vars.n
        posts = e6.get(tags=tags, n=n)
        msg_template = '{} - {}'
        msg = StringBuilder(sep='\n')
        images = [post for post in posts if post['ext'] in ['jpg', 'png', 'jpeg']]
        msg += 'Вот йифф по твоему запросу'
        while len(images)>0:
            chunk = []
            if len(images)>10:
                chunk = images[:10]
                images = images[10:]

            elif len(images)<=10:
                chunk = images
                images = []
            print(chunk)
            msg.add_list(list([msg_template.format(n+1, post['url']) for n, post in enumerate(chunk)]))
            att = self.api.UploadPhoto([post['url'] for post in chunk])
            data.send_back(msg.toString(), att, True)
            msg.purge()
            sleep(0.5)
        LOGGER.info('Прон кончился')
        return True


@ModuleManager.command(names=["e926"], perm='photo.e926', desc="Ищет пикчи на e612",
                       template="Ищет пикчи на e926, форма запроса:\n" \
                                "{botname}, e926\n" \
                                "tags:тэги через ;\n" \
                                "sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n" \
                                "n:кол-во артов(максимум 10)\n" \
                                "page:страница на которой искать", cost=15)
@ModuleManager.argument('tags', '', 'Тэги через ";"', Yes)
@ModuleManager.argument('n', 5, 'Кол-во фото', No,30)
class Command_e926(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        tags = self.vars.tags.strip().split(';')
        n = self.vars.n
        posts = e6.getSafe(tags=tags, n=n)
        msg_template = '{} - {}'
        msg = StringBuilder(sep = '\n')
        images = [post for post in posts if post['ext'] in ['jpg', 'png', 'jpeg']]
        msg += 'Вот фуррятина по твоему запросу'
        while len(images)>0:
            if len(images)>10:
                chunk = images[:10]
                images = images[10:]

            elif len(images)<10:
                chunk = images
                images = []
            msg.add_list(list([msg_template.format(n+1, post['url']) for n, post in enumerate(chunk)]))
            att = self.api.UploadPhoto([post['url'] for post in chunk])
            data.send_back(msg.toString(), att, True)
            msg.purge()
            sleep(0.5)


        return True


@ModuleManager.command(names=["rollrows"], perm='photo.rollRows', desc="Сдвигает строки в фото")
@ModuleManager.argument('delta', 20, 'Сила смещений', False)
class Command_rollRows(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        delta = self.vars.delta

        Topost = []
        for att in data.attachments:
            try:
                photo = att.photo.GetHiRes
            except:
                return False

            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            roll(Tmp.path_, delta)
            Tmp.cachefile(Tmp.path_)
            att = self.api.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.rem()
        data.send_back(":D", Topost, True)


@ModuleManager.command(names=["rollsmart"], perm='photo.rollRowssmart', desc="Сдвигает строки в фото")
@ModuleManager.argument('delta', 20, 'Сила смещений', False)
class Command_rollRowssmart(C_template):
    @staticmethod
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        delta = self.vars.delta

        Topost = []
        for att in data.attachments:
            try:
                photo = att.photo.GetHiRes
            except:
                return False

            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            rollsmast(Tmp.path_)
            Tmp.cachefile(Tmp.path_)
            att = self.api.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.rem()
        data.send_back(":D", Topost, True)


@ModuleManager.command(names=["сложи"], perm='photo.add', desc="Соединяет 2 фото")
class Command_AddImages(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        atts = data.attachments
        if len(atts) < 2:
            args.message = 'Нужны 2 файла'
            self.api.Replyqueue.put(args)


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
        add(Tmp.path_, Tmp1.path_)
        att = self.api.UploadFromDisk(Tmp.path_)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        data.send_back(":D", [att], True)


@ModuleManager.command(names=["совмести"], perm='photo.merge', desc="Соединяет 2 фото")
class Command_merge(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        atts = data.attachments
        # print(atts)
        if len(atts) < 2:
            args.message = 'Нужны 2 файла'
            self.api.Replyqueue.put(args)
            return


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
        Merge(Tmp.path_, Tmp1.path_)
        att = self.api.UploadFromDisk(Tmp.path_)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        data.send_back(":D", [att], True)


@ModuleManager.command(names=["скрин"], perm='core.screen', desc="Скрин экрана")
class Command_screen(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        im = ImageGrab.grab()
        pt = TempFile.generatePath('jpg')
        im.save(pt)
        att = self.api.UploadFromDisk(pt)
        print(att)
        os.remove(pt)
        data.send_back('Ееее, скрины', [att], True)


@ModuleManager.command(names=["глитч"], perm='photo.glitch', desc="Глючит фото")
class Command_GlitchImg(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        Topost = []

        for att in data.attachments:
            try:
                photo = att.photo.GetHiRes
            except:
                return False
            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            Glitch2.glitch_an_image(Tmp.path_)
            att = self.api.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        data.send_back('Меня одного глючит?', Topost, True)


#@ModuleManager.command(names=["everypixel"], perm='photo.everypixel', desc='Описывает ваше фото')
class Command_everyPixel(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        att = data.attachments[0]
        photo = att.photo.GetHiRes
        req = urllib.request.Request(photo, headers=HDR)
        img = urlopen(req).read()
        Tmp = TempFile(img, 'jpg')
        tags, quality = EveryPixel.GetTags(Tmp.path_)
        tags_template = 'Я вижу тут:\n{}\n'
        tags_msg = tags_template.format('\n'.join(tags))

        msg = tags_msg + 'Годнота этой пикчи - {}\n'.format(int(quality))
        data.send_back(msg, [], True)


@ModuleManager.command(names=["маска", 'цензура'], perm='core.mask', desc="маскирует фото")
class Mask_photo(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):

        if self.api.remixsed == 0 or not self.api.remixsed_avalible:
            msg = 'Невозможно выполнить так-как нету печенек :C'
            data.send_back(msg, [], True)
            return
        atts = data.attachments  # type: list[attachment]
        # print(atts)
        if len(atts) < 2:
            msg = 'Нужны 2 файла'
            data.send_back(msg, [], True)
            return
        Topost = []

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
        Tmp500 = TempFile(img, 'jpg')
        Tmp1000 = TempFile(img1, 'jpg')
        img1 = Image.open(open(Tmp500.path_, 'rb'))
        img1 = resize_(500, img1, ret=True)
        img1.save(Tmp500.path_)
        img2 = Image.open(open(Tmp1000.path_, 'rb'))
        img2 = resize_(1000, img2, ret=True)
        img2.save(Tmp1000.path_)

        pid_ = self.api.UploadFromDisk(Tmp500.path_)
        owner, pid_ = pid_[5:].split('_')
        msg = 'Ща всё будет'
        # args.attachment = [f'photo{owner}_{pid_}']
        data.send_back(msg, [], True)
        c = 0

        def replace(c):
            try:
                replacePhoto(f'{owner}_{pid_}', Tmp500.path_, self.api.remixsed)
                replacePhoto(f'{owner}_{pid_}', Tmp1000.path_, self.api.remixsed)
                img2 = Image.open(open(Tmp1000.path_, 'rb'))
                img2 = resize_(1500, img2, ret=True)
                img2.save(Tmp1000.path_)
                replacePhoto(f'{owner}_{pid_}', Tmp1000.path_, self.api.remixsed)
                replacePhoto(f'{owner}_{pid_}', Tmp500.path_, self.api.remixsed)
            except:
                c += 1
                if c > 2:

                    msg = 'Чёто пошло совсем не так'
                    data.send_back(msg, [], True)
                    return
                self.api.check_remixsid(force=True)
                replace(c)

        replace(c)
        self.api.UserApi.photos.delete(owner_id=owner, photo_id=pid_)
        self.api.UserApi.photos.restore(owner_id=owner, photo_id=pid_)
        Tmp500.cachefile(Tmp500.path_)
        Tmp1000.cachefile(Tmp1000.path_)
        Tmp500.rem()
        Tmp1000.rem()
        msg = 'Вотъ'
        # args.attachment = []
        att = [f'photo{owner}_{pid_}']
        data.send_back(msg, [], True)


from libs.imgur import Imgur


@ModuleManager.command(['найди'], perm='core.imgur', desc="ищет файлы")
class ImgurAPI(C_template):
    def sub_init(self):
        self.imgur = Imgur()

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        imgs = self.imgur.get(q=' '.join(data.args))
        imgs = imgs[:10]
        # print(imgs)
        atts = []
        try:
            photo = self.api.UploadPhoto([a for a in imgs if a.split('.')[-1] in ['jpg', 'png']])
            atts.extend(photo)
        except:
            pass
        try:
            doc = self.api.UploadDocsDisk([a for a in imgs if a.split('.')[-1] in ['gif']])
            atts.extend(doc)
        except:
            pass
            data.send_back("0_o", atts, True)
