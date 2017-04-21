import os
import re
import traceback
import urllib
from urllib.request import urlopen

import sys

from CustomPrint import print_
from DataTypes.attachments import attachment
from Module_manager_v2 import ModuleManager
from libs.photo_replacer import replacePhoto
from trigger import Trigger

try:

    from PIL import ImageGrab, Image

    windows = True
except ImportError:
    windows = False
    ImageGrab = None

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
    name = ["кок"]
    access = ["all"]
    desc = "Зеркалит картинку"
    perm = 'photo.kok'

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
                kok(Tmp.path_)
                att = self.api.UploadFromDisk(Tmp.path_)
                Tmp.cachefile(Tmp.path_)
                Tmp.rem()
                args.attachment = att
                self.api.Replyqueue.put(args)
            return True
        except:
            return False


@ModuleManager.command(names=["кек"], perm='photo.kek', desc="Зеркалит картинку", cost=2)
class Command_Kek(C_template):
    name = ["кек"]
    access = ["all"]
    desc = "Зеркалит картинку"
    perm = 'photo.kek'

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
                kek(Tmp.path_)
                att = self.api.UploadFromDisk(Tmp.path_)
                Tmp.cachefile(Tmp.path_)
                Tmp.rem()
                args.attachment = att
                self.api.Replyqueue.put(args)
                return True
        except:
            return False


@ModuleManager.command(names=["обработай", 'фильтр'], perm='photo.filter', desc="Позволяет применять фильтры к фото",
                       cost=2)
class Command_Filter(C_template):
    name = ["обработай", 'фильтр']
    access = ["all"]
    desc = "Позволяет применять фильтры к фото"
    perm = 'photo.filter'
    cost = 15

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
                args.message = 'Список фильтров:\n'
                FArr = dict(enumerate(self.api.MODULES.FILTERS))
                for filter_ in FArr:
                    Fname = self.api.MODULES.FILTERS[FArr[filter_]].desc
                    args.message += "{}. {}\n".format(filter_ + 1, Fname)
                self.api.Replyqueue.put(args)

                t = Trigger(cond=lambda
                    Tdata: Tdata.user_id == data.user_id and Tdata.chat_id == data.chat_id and Tdata.body.isnumeric(),
                            callback=self.Render, Tmp=Tmp, bot=self.api, args=args, FArr=FArr)
                self.api.TRIGGERS.addTrigger(t)
                return True
        except Exception as Ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            TB = traceback.format_tb(exc_traceback)
            print_(exc_type, exc_value, traceback.print_tb(exc_traceback))
            return False

    def Render(self, data: LongPoolHistoryMessage, result, Tmp, bot: Vk_bot2.Bot, args: ArgBuilder.Args_message, FArr):
        if result == False:
            Tmp.rem()
            args.message = "Время ожидания ответа истекло"
            self.api.Replyqueue.put(args)
            return
        ans = int(data.body) - 1
        filter_ = self.api.MODULES.FILTERS[FArr[ans]].funk
        print('used filter {}'.format(filter_.name))
        filter_().render(Tmp.path_)

        args.message = filter_.name
        print(args)
        Tmp.cachefile(Tmp.path_)
        args.attachment = [self.api.UploadFromDisk(Tmp.path_)]
        Tmp.rem()

        self.api.Replyqueue.put(args)
        return


@ModuleManager.command(names=["увеличь"], perm='photo.resize', desc="Позволяет увеличивать\уменьшать фото")
class Command_Resize(C_template):
    name = ["увеличь"]
    access = ["all"]
    desc = "Позволяет увеличивать\уменьшать фото"
    perm = 'photo.resize'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        if 'size' in data.custom:
            x = int(data.custom['size'])
            if x > 3000:
                args.message = "Неее, слишком жирно"
                self.api.Replyqueue.put(args)
                return False
        else:
            args.message = "Размер не указан"
            self.api.Replyqueue.put(args)
            return False
        Topost = []
        for att in data.attachments:
            try:
                photo = att.photo.GetHiRes
            except:
                return False
            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg', NoCache=True)
            args.message = 'Поднимать резкость?\n Да\Нет'
            self.api.Replyqueue.put(args)
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
        args.message = "Вотъ"
        args.message = [self.api.UploadFromDisk(Tmp.path_)]
        Tmp.cachefile(Tmp.path_)
        Tmp.rem()
        self.api.Replyqueue.put(args)


from bs4 import *


@ModuleManager.command(names=["e621"], perm='core.e621', desc="Ищет пикчи на e612",
                       template="Ищет пикчи на e612, форма запроса:\n"\
                                "{botname}, e621\n"\
                                "tags:тэги через ;\n"\
                                "sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n"\
                                "n:кол-во артов(максимум 10)\n"\
                                "page:страница на которой искать")
class Command_e621(C_template):
    name = ["e621"]
    access = ["admin", "editor", "moderator"]
    desc = "Ищет пикчи на e612"
    perm = 'core.e621'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        data.custom['tags'] = BeautifulSoup(data.custom['tags'], "html.parser").get_text()
        tags = data.custom['tags'].replace(' ', '').split(';') if 'tags' in data.custom else None
        if tags == None:
            args.message = Command_e926.info
            self.api.Replyqueue.put(args)
            return True
        n = int(data.custom['n']) if 'n' in data.custom else 5
        page = int(data.custom['page']) if 'page' in data.custom else 1
        sort_ = data.custom['sort'].replace(' ', '') if 'sort' in data.custom else 'score'
        posts = e6.get(tags=tags, n=n, page=page, sort_=sort_)
        msg_template = '{} - {}\n'
        msg = ""
        atts = []
        for n, post in enumerate(posts):
            # msg += msg_template.format(n + 1, post['link'], '\n'.join(post['sources']))
            msg += msg_template.format(n + 1, post['link'], )
        for post in posts:
            if post['ext'] not in ['jpg', 'png', 'jpeg']:
                continue
            atts.append(self.api.UploadPhoto(post['url']))
        args.attachment = atts
        args.message = 'Вот порнушка по твоему запросу, шалунишка...\n' + msg
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=["e926"], perm='photo.e926', desc="Ищет пикчи на e612",
                       template="Ищет пикчи на e926, форма запроса:\n"\
                                "{botname}, e926\n"\
                                "tags:тэги через ;\n"\
                                "sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n"\
                                "n:кол-во артов(максимум 10)\n"\
                                "page:страница на которой искать",cost=15)
class Command_e926(C_template):
    name = ["e926"]
    access = ["all"]
    info = """Ищет пикчи на e926, форма запроса:\n
           Ред, e926\n
           tags:тэги через ;\n
           sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n
           n:кол-во артов(максимум 10)\n
           page:страница на которой искать"""
    desc = "Ищет пикчи на e926"
    perm = 'photo.e926'
    cost = 15

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        data.custom['tags'] = BeautifulSoup(data.custom['tags'], "html.parser").get_text()
        tags = data.custom['tags'].replace(' ', '').split(';') if 'tags' in data.custom else None
        if tags == None:
            args.message = Command_e926.info
            self.api.Replyqueue.put(args)
            return True
        n = int(data.custom['n']) if 'n' in data.custom else 5
        page = int(data.custom['page']) if 'page' in data.custom else 1
        sort_ = data.custom['sort'].replace(' ', '') if 'sort' in data.custom else 'score'
        posts = e6.getSafe(tags=tags, n=n, page=page, sort_=sort_)
        msg_template = '{} - {}\n'
        msg = ""
        for n, post in enumerate(posts):
            # msg += msg_template.format(n + 1, post['link'], '\n'.join(post['sources']))
            msg += msg_template.format(n + 1, post['link'], )

        atts = []
        for post in posts:
            if post['ext'] not in ['jpg', 'png', 'jpeg']:
                continue
            atts.append(self.api.UploadPhoto(post['url']))
        args.attachment = atts
        args.message = 'Вот пикчи по твоему запросу\n' + msg
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=["rollrows"], perm='photo.rollRows', desc="Сдвигает строки в фото")
class Command_rollRows(C_template):
    name = ["rollrows"]
    access = ["all"]
    desc = "Сдвигает строки в фото"
    perm = 'photo.rollRows'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        delta = int(data.custom['delta']) if 'delta' in data.custom else 20

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
        args.attachment = Topost
        args.message = ':D'
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=["rollsmart"], perm='photo.rollRowssmart', desc="Сдвигает строки в фото")
class Command_rollRowssmart(C_template):
    name = ["rollsmart"]
    access = ["all"]
    desc = "Сдвигает строки в фото"
    perm = 'photo.rollRowssmart'

    @staticmethod
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        delta = int(data.custom['delta']) if 'delta' in data.custom else 20

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
        args.attachment = Topost
        args.message = ':D'
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=["сложи"], perm='photo.add', desc="Соединяет 2 фото")
class Command_AddImages(C_template):
    name = ["сложи"]
    access = ['all']
    desc = "Соединяет 2 фото"
    perm = 'photo.add'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        atts = data.attachments
        if len(atts) < 2:
            args.message = 'Нужны 2 файла'
            self.api.Replyqueue.put(args)
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
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        add(Tmp.path_, Tmp1.path_)
        att = self.api.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        args.message = ':D'
        args.attachment = Topost
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=["совмести"], perm='photo.merge', desc="Соединяет 2 фото")
class Command_merge(C_template):
    name = ["совмести"]
    access = ['all']
    desc = "Соединяет 2 фото"
    perm = 'photo.merge'

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
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        Merge(Tmp.path_, Tmp1.path_)
        att = self.api.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        args.message = ':D'
        args.attachment = Topost
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=["скрин"], perm='core.screen', desc="Скрин экрана")
class Command_screen(C_template):
    enabled = windows
    name = ["скрин"]
    access = ['admin']
    desc = "Скрин экрана"
    perm = 'core.screen'


    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        im = ImageGrab.grab()
        pt = TempFile.generatePath('jpg')
        im.save(pt)
        att = self.api.UploadFromDisk(pt)
        os.remove(pt)
        args.message = 'Ееее, скрины'
        args.attachment = att
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=["глитч"], perm='photo.glitch', desc="Глючит фото")
class Command_GlitchImg(C_template):
    name = ["глитч"]
    access = ["all"]
    desc = "Глючит фото"
    perm = 'photo.glitch'
    cost = 0


    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
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
        args.message = 'Меня одного глючит?'
        args.attachment = Topost
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=["everypixel"], perm='photo.everypixel', desc='Описывает ваше фото')
class Command_everyPixel(C_template):
    name = ['everypixel']
    access = ['all']
    desc = 'Описывает ваше фото'
    perm = 'photo.everypixel'


    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        att = data.attachments[0]
        photo = att.photo.GetHiRes
        req = urllib.request.Request(photo, headers=HDR)
        img = urlopen(req).read()
        Tmp = TempFile(img, 'jpg')
        tags, quality = EveryPixel.GetTags(Tmp.path_)
        tags_template = 'Я вижу тут:\n{}\n'
        tags_msg = tags_template.format('\n'.join(tags))

        args.message = tags_msg + 'Годнота этой пикчи - {}\n'.format(int(quality))
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=["маска",'цензура'], perm='core.mask', desc="маскирует фото")
class Mask_photo(C_template):


    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):

        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        if self.api.remixsed == 0:
            args.message = 'Невозможно выполнить так-как нету печенек :C'
            self.api.Replyqueue.put(args)
            return
        atts = data.attachments #type: list[attachment]
        # print(atts)
        if len(atts) < 2:
            args.message = 'Нужны 2 файла'
            self.api.Replyqueue.put(args)
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
        img1 = Image.open(open(Tmp500.path_,'rb'))
        img1 = resize_(500,img1,ret=True)
        img1.save(Tmp500.path_)
        img2 = Image.open(open(Tmp1000.path_,'rb'))
        img2 = resize_(1500, img2, ret=True)
        img2.save(Tmp1000.path_)

        pid_ = self.api.UploadFromDisk(Tmp500.path_)
        print(pid_)
        owner, pid_ = pid_[5:].split('_')
        args.message = 'Ща всё будет'
        #args.attachment = [f'photo{owner}_{pid_}']
        self.api.Replyqueue.put(args)

        replacePhoto(f'{owner}_{pid_}',Tmp500.path_,self.api.remixsed)
        replacePhoto(f'{owner}_{pid_}',Tmp1000.path_,self.api.remixsed)
        img2 = Image.open(open(Tmp1000.path_, 'rb'))
        img2 = resize_(1500, img2, ret=True)
        img2.save(Tmp1000.path_)
        replacePhoto(f'{owner}_{pid_}',Tmp1000.path_,self.api.remixsed)
        replacePhoto(f'{owner}_{pid_}',Tmp500.path_,self.api.remixsed)

        self.api.UserApi.photos.delete(owner_id = owner, photo_id = pid_)
        self.api.UserApi.photos.restore(owner_id = owner, photo_id = pid_)
        Tmp500.cachefile(Tmp500.path_)
        Tmp1000.cachefile(Tmp1000.path_)
        Tmp500.rem()
        Tmp1000.rem()
        args.message = 'Вотъ'
        #args.attachment = []
        args.attachment = [f'photo{owner}_{pid_}']
        self.api.Replyqueue.put(args)