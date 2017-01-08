import random
import urllib
from urllib.request import urlopen

import DA_Api as D_A
import Vk_bot_RssModule
import YT_Api as YT_
import e621_Api as e6
from GlitchLib import Merge
from PIL_module import kok, kek, roll, rollRandom, rollsmast, add
from tempfile_ import TempFile

HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


class Command_Whom:
    name = "кого"
    access = ["all"]

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        if int(data['peer_id']) <= 2000000000:
            args['message'] = "Тебя"
            return args
        else:
            chat = int(data['peer_id']) - 2000000000
            users = bot.UserApi.messages.getChatUsers(chat_id=chat, fields='nickname', v=5.38,
                                                      name_case='acc')
            user = random.choice(users)
            if user['id'] == bot.MyUId:
                args['message'] = 'Определённо меня'
                bot.Replyqueue.put(args)
            name = '{} {}'.format(user['first_name'], user['last_name'])
            replies = ["Определённо {}", "Точно {}", "Я уверен что его -  {}"]
            msg = random.choice(replies)
            args['message'] = msg.format(name)
            # self.Reply(self.UserApi, args)
            bot.Replyqueue.put(args)


class Command_Who:
    name = "кто"
    access = ["all"]

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        text = " ".join(data['message'].split(',')[1].split(' ')[2:]) if "?" not in data['message'] else " ".join(
            data['message'].split(',')[1].split(' ')[2:])[:-1]
        if "мне" in text: text = text.replace('мне', 'тебе')
        if "мной" in text: text = text.replace('мной', 'тобой')
        if "моей" in text: text = text.replace('моей', 'твоей')
        if int(data['peer_id']) <= 2000000000:
            args['message'] = "Ты"
            bot.Replyqueue.put(args)
        else:
            chat = int(data['peer_id']) - 2000000000
            users = bot.UserApi.messages.getChatUsers(chat_id=chat, fields='nickname', v=5.38,
                                                      name_case='nom')
            user = random.choice(users)
            if user['id'] == bot.MyUId:
                args['message'] = 'Определённо Я'
                bot.Replyqueue.put(args)
            name = '{} {}'.format(user['first_name'], user['last_name'])
            replies = ["Определённо {} {}", "Точно {} {}", "Я уверен что он -  {} {}"]
            msg = random.choice(replies)
            args['message'] = msg.format(name, text)
            # self.Reply(self.UserApi, args)
            bot.Replyqueue.put(args)


class Command_Prob:
    name = "вероятность"
    access = ["all"]

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        a = data['message'].split(' ')
        if 'вероятность' in a[1]:
            a = a[2:]
        else:
            a = a[1:]
        msg = "Вероятность того, что {}, равна {}%".format(' '.join(a), random.randint(0, 100))
        args['message'] = msg
        # self.Reply(self.UserApi, args)
        bot.Replyqueue.put(args)


class Command_Where:
    name = "где"
    access = ["all"]

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        replies = ["Под столом", "На кровати", "За спиной", "На столе"]
        msg = random.choice(replies)
        args['message'] = msg
        # self.Reply(self.UserApi, args)
        bot.Replyqueue.put(args)


class Command_Kok:
    name = "кок"
    access = ["all"]

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

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        atts = bot.UserApi.messages.getById(message_id=data['message_id'])[1]['attachments']
        Topost = []

        for att in atts:
            try:
                att = data['attachments'][0]
                photo = bot.GetBiggesPic(att, data['message_id'])
            except:
                return False
            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg', NoCache=True)
            m = ''
            print()
            FiltersArray = list(bot.Botmodules['filters'].values())
            for i in range(len(FiltersArray)):
                m += "{}.{}\n".format(i + 1, FiltersArray[i].name)
            args['message'] = 'Список фильтров:\n' + m
            args['forward_messages'] = data['message_id']
            bot.Replyqueue.put(args)
            ans = bot.WaitForMSG(5, data)
            print('used filter {}'.format(ans - 1))
            ImgF = FiltersArray[ans - 1]()
            ImgF.render(Tmp.path_)
            args['message'] = 'Фильтр {}'.format(FiltersArray[ans - 1].name)
            att = bot.UploadFromDisk(Tmp.path_)

            Topost.append(att)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        args['forward_messages'] = data['message_id']
        bot.Replyqueue.put(args)


class Command_e621:
    name = "e621"
    access = ["admin", "editor", "moderator"]
    info = """Ищет пикчи на e612, форма запроса:\n
           !e621\n
           tags:тэги через ;\n
           sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n
           n:кол-во артов(максимум 10)\n
           page:страница на которой искать"""

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

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        delta = int(args['delta']) if 'delta' in data['custom'] else 20
        atts = bot.UserApi.messages.getById(message_id=args['data']['message_id'])[1]['attachments']
        Topost = []
        for att in atts:
            try:
                att = data['attachments'][0]
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


class Command_rollRowsrand:
    name = "rollrowsrand"
    access = ["all"]

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        delta = int(args['delta']) if 'delta' in data['custom'] else 20
        atts = bot.UserApi.messages.getById(message_id=args['data']['message_id'])[1]['attachments']
        Topost = []
        for att in atts:
            try:
                att = data['attachments'][0]
                photo = bot.GetBiggesPic(att, data['message_id'])
            except:
                return False

            req = urllib.request.Request(photo, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            rollsmast(Tmp.path_, delta)
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
