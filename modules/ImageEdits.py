import os
import re
import urllib
from urllib.request import urlopen

from PIL import ImageGrab

import e621_Api as e6
from GlitchLib import Merge
from PIL_module import kok, kek, roll, rollsmast, add, resize_, Glitch2
from tempfile_ import TempFile

HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


class Command_Kok:
    name = "кок"
    access = ["all"]
    desc = "Зеркалит картинку"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        try:
            att = data['attachments'][0]
            print(att)
            photo = bot.GetBiggesPic(att, data['message_id'])
        except:
            return False
        req = urllib.request.Request(photo, headers=HDR)
        img = urlopen(req).read()
        Tmp = TempFile(img, 'jpg', NoCache=True)
        kok(Tmp.path_)
        att = bot.UploadFromDisk(Tmp.path_)
        Tmp.cachefile(Tmp.path_)
        Tmp.rem()
        args['attachment'] = att
        bot.Replyqueue.put(args)


class Command_Kek:
    name = "кек"
    access = ["all"]
    desc = "Зеркалит картинку"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        try:
            att = data['attachments'][0]
            print(att)
            photo = bot.GetBiggesPic(att, data['message_id'])
        except:
            return False
        req = urllib.request.Request(photo, headers=HDR)
        img = urlopen(req).read()
        Tmp = TempFile(img, 'jpg', NoCache=True)
        kek(Tmp.path_)
        att = bot.UploadFromDisk(Tmp.path_)
        Tmp.cachefile(Tmp.path_)
        Tmp.rem()
        args['attachment'] = att
        bot.Replyqueue.put(args)


class Command_Filter:
    name = "обработай"
    access = ["all"]
    desc = "Позволяет применять фильтры к фото"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        atts = data['attachments']
        Topost = []
        for att in atts:
            try:
                photo = bot.GetBiggesPic(att, data['message_id'])
            except:
                return False
            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg', NoCache=True)
            args['message'] = 'Список фильтров:\n'
            FArr = dict(enumerate(bot.FILTERS))
            for filter_ in FArr:
                Fname = bot.FILTERS[FArr[filter_]].name
                args['message'] += "{}. {}\n".format(filter_ + 1, Fname)
            bot.Replyqueue.put(args)

            ans = int(bot.WaitForMSG(5, data)) - 1
            if ans == None:
                Tmp.rem()
                args['message'] = "Время ожидания ответа истекло"
                bot.Replyqueue.put(args)
            filter_ = bot.FILTERS[FArr[ans]]

            print('used filter {} {}'.format(ans, filter_.name))

            filter_().render(Tmp.path_)

            args['message'] = filter_.name

            Topost.append(bot.UploadFromDisk(Tmp.path_))
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        bot.Replyqueue.put(args)


class Command_Resize:
    name = "увеличь"
    access = ["all"]
    desc = "Позволяет увеличивать\уменьшать фото"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        atts = data['attachments']
        if 'size' in data['custom']:
            x = int(data['custom']['size'])
            if x > 3000:
                args['message'] = "Неее, слишком жирно"
                bot.Replyqueue.put(args)
                return False
        else:
            args['message'] = "Размер не указан"
            bot.Replyqueue.put(args)
            return False
        Topost = []
        for att in atts:
            try:
                photo = bot.GetBiggesPic(att, data['message_id'])
            except:
                return False
            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg', NoCache=True)
            args['message'] = 'Поднимать резкость?\n Да\Нет'
            bot.Replyqueue.put(args)
            ans = bot.WaitForMSG(5, data)
            if ans == None:
                Tmp.rem()
                args['message'] = "Время ожидания ответа истекло"
                bot.Replyqueue.put(args)
            sharp = False
            if re.match(r'(Д|д)а', ans):
                sharp = True
            elif re.match(r'(Н|н)ет', ans):
                sharp = False
            resize_(x, Tmp.path_, sharp)
            args['message'] = "Вотъ"

            Topost.append(bot.UploadFromDisk(Tmp.path_))
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        bot.Replyqueue.put(args)


class Command_e621:
    name = "e621"
    access = ["admin", "editor", "moderator"]
    info = """Ищет пикчи на e612, форма запроса:\n
           Ред, e621\n
           tags:тэги через ;\n
           sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n
           n:кол-во артов(максимум 10)\n
           page:страница на которой искать"""
    desc = "Ищет пикчи на e612"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        tags = data['custom']['tags'].replace(' ', '').split(';') if 'tags' in data['custom'] else None
        if tags == None:
            args['message'] = Command_e926.info
            bot.Replyqueue.put(args)
            return True
        n = int(data['custom']['n']) if 'n' in data['custom'] else 5
        page = int(data['custom']['page']) if 'page' in data['custom'] else 1
        sort_ = data['custom']['sort'].replace(' ', '') if 'sort' in data['custom'] else 'score'
        imgs = e6.get(tags=tags, n=n, page=page, sort_=sort_)
        print(imgs)
        atts = bot.UploadPhoto(imgs)
        args['attachment'] = atts
        args['message'] = 'Вот порнушка по твоему запросу, шалунишка...'
        bot.Replyqueue.put(args)


class Command_e926:
    name = "e926"
    access = ["all"]
    info = """Ищет пикчи на e926, форма запроса:\n
           !e926\n
           tags:тэги через ;\n
           sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n
           n:кол-во артов(максимум 10)\n
           page:страница на которой искать"""
    desc = "Ищет пикчи на e926"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        tags = data['custom']['tags'].replace(' ', '').split(';') if 'tags' in data['custom'] else None
        if tags == None:
            args['message'] = Command_e926.info
            bot.Replyqueue.put(args)
            return True
        n = int(data['custom']['n']) if 'n' in data['custom'] else 5
        page = int(data['custom']['page']) if 'page' in data['custom'] else 1
        sort_ = data['custom']['sort'].replace(' ', '') if 'sort' in data['custom'] else 'score'
        imgs = e6.getSafe(tags=tags, n=n, page=page, sort_=sort_)
        print(imgs)
        atts = bot.UploadPhoto(imgs)
        args['attachment'] = atts
        args['message'] = 'Вот пикчи по твоему запросу'
        bot.Replyqueue.put(args)


class Command_rollRows:
    name = "rollrows"
    access = ["all"]
    desc = "Сдвигает строки в фото"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        delta = int(args['delta']) if 'delta' in data['custom'] else 20
        atts = data['attachments']
        Topost = []
        for att in atts:
            try:
                photo = bot.GetBiggesPic(att, data['message_id'])
            except:
                return False

            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            roll(Tmp.path_, delta)
            Tmp.cachefile(Tmp.path_)
            att = bot.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.rem()
        args['attachment'] = Topost
        args['message'] = ':D'
        bot.Replyqueue.put(args)


class Command_rollRowssmart:
    name = "rollsmart"
    access = ["all"]
    desc = "Сдвигает строки в фото"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        delta = int(args['delta']) if 'delta' in data['custom'] else 20
        atts = data['attachments']
        Topost = []
        for att in atts:
            try:
                photo = bot.GetBiggesPic(att, data['message_id'])
            except:
                return False

            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            rollsmast(Tmp.path_)
            Tmp.cachefile(Tmp.path_)
            att = bot.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.rem()
        args['attachment'] = Topost
        args['message'] = ':D'
        bot.Replyqueue.put(args)


class Command_AddImages:
    name = "сложи"
    access = ['all']
    desc = "Соединяет 2 фото"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        atts = data['attachments']
        # print(atts)
        if len(atts) < 2:
            args['message'] = 'Нужны 2 файла'
            bot.Replyqueue.put(args)
        Topost = []

        try:

            photo = bot.GetBiggesPic(atts[0], data['message_id'])
        except:
            return False
        try:
            photo1 = bot.GetBiggesPic(atts[1], data['message_id'])
        except:
            return False
        req = urllib.request.Request(photo, headers=HDR)
        req1 = urllib.request.Request(photo1, headers=HDR)
        img = urlopen(req).read()
        img1 = urlopen(req1).read()
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        add(Tmp.path_, Tmp1.path_)
        att = bot.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        args['attachment'] = Topost
        bot.Replyqueue.put(args)


class Command_merge:
    name = "совмести"
    access = ['all']
    desc = "Соединяет 2 фото"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        atts = data['attachments']
        # print(atts)
        if len(atts) < 2:
            args['message'] = 'Нужны 2 файла'
            bot.Replyqueue.put(args)
        Topost = []

        try:

            photo = bot.GetBiggesPic(atts[0], data['message_id'])
        except:
            return False
        try:
            photo1 = bot.GetBiggesPic(atts[1], data['message_id'])
        except:
            return False
        req = urllib.request.Request(photo, headers=HDR)
        req1 = urllib.request.Request(photo1, headers=HDR)
        img = urlopen(req).read()
        img1 = urlopen(req1).read()
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        Merge(Tmp.path_, Tmp1.path_)
        att = bot.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        args['attachment'] = Topost
        bot.Replyqueue.put(args)


class Command_screen:
    name = "скрин"
    access = ['admin']
    desc = "Скрин экрана"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        im = ImageGrab.grab()
        pt = TempFile.generatePath('jpg')
        im.save(pt)
        att = bot.UploadFromDisk(pt)
        os.remove(pt)
        args['attachment'] = att
        bot.Replyqueue.put(args)


class Command_GlitchImg:
    name = "глитч"
    access = ["all"]
    desc = "Глючит фото"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        atts = data['attachments']
        Topost = []

        for att in atts:
            try:
                photo = bot.GetBiggesPic(att, data['message_id'])
            except:
                return False
            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            Glitch2.glitch_an_image(Tmp.path_)
            att = bot.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        bot.Replyqueue.put(args)
