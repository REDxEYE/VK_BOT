import importlib
import os
import random
import threading
import types
import urllib
from datetime import datetime, timedelta
from html.parser import HTMLParser
from math import log
from time import sleep
from urllib.request import urlopen

import feedparser
import pymorphy2
from vk import API

from Vk_bot2 import SessionCapchaFix
from tempfile_ import TempFile

morph = pymorphy2.MorphAnalyzer()
HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def getpath():
    return os.path.dirname(os.path.abspath(__file__))


def prettier_size(n, pow=0, b=1024, u='B', pre=[''] + [p + 'i' for p in 'KMGTPEZY']):
    r, f = min(int(log(max(n * b ** pow, 1), b)), len(pre) - 1), '{:,.%if} %s%s'
    return (f % (abs(r % (-r - 1)), pre[r], u)).format(n * b ** pow / b ** float(r))


class Command_Whom:
    name = "кого"
    access = ["all"]
    desc = "Выбирает случайного человека"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        text = " ".join(data['message'].split(',')[1].split(' ')[2:]) if "?" not in data['message'] else " ".join(
            data['message'].split(',')[1].split(' ')[2:])[:-1]
        if int(data['peer_id']) <= 2000000000:
            args['message'] = "Тебя"
            return args
        else:
            chat = int(data['peer_id']) - 2000000000
            users = bot.UserApi.messages.getChatUsers(chat_id=chat, fields='nickname', v=5.38,
                                                      name_case='acc')
            toinf = text.split(" ")
            toins = ""
            user = random.choice(users)
            ud = bot.GetUserNameById(user['id'])['sex']
            if ud == 2:
                userGender = "masc"
            elif ud == 1:
                userGender = "femn"
            else:
                userGender = "neut"
            for wrd in toinf:
                print(wrd)
                toinfwrd = morph.parse(wrd)[0]
                if ('VERB' or "NPRO") in toinfwrd.tag.POS:
                    try:

                        if toinfwrd.normal_form == "я":
                            print("Ja", toinfwrd)
                            toinfwrd = morph.parse("ты")[0]
                            infwrd = toinfwrd.inflect({"accs", "2per"})
                        else:
                            infwrd = toinfwrd.inflect({userGender, toinfwrd.tag.POS})
                        print(infwrd)
                        toins += "{} ".format(str(infwrd.word))
                    except:
                        print("err", wrd)
                else:
                    toins += "{} ".format(wrd)

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
    name = "кто?"
    access = ["all"]
    desc = "Выбирает случайного человека"

    @staticmethod
    def execute(bot, data, ):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        text = " ".join(
            data['message'].split(',')[1].split(' ')[2:])[:-1] if data['message'].endswith("?") else " ".join(
            data['message'].split(',')[1].split(' ')[2:])
        if "мне" in text: text = text.replace('мне', 'тебе')
        if "мной" in text: text = text.replace('мной', 'тобой')
        if "моей" in text: text = text.replace('моей', 'твоей')
        if int(data['peer_id']) <= 2000000000:
            args['message'] = "Ты"
            bot.Replyqueue.put(args)
            return True
        else:
            chat = int(data['peer_id']) - 2000000000
            users = bot.UserApi.messages.getChatUsers(chat_id=chat, fields='nickname', v=5.60,
                                                      name_case='nom')

            user = random.choice(users)
            ud = bot.GetUserNameById(user['id'])['sex']
            if ud == 2:
                userGender = "masc"
            elif ud == 1:
                userGender = "femn"
            else:
                userGender = "neut"
            print("UserGender:", userGender)
            toinf = text.split(" ")
            toins = ""
            for wrd in toinf:
                print(wrd)
                toinfwrd = morph.parse(wrd)[0]
                try:
                    if ('VERB' or "NPRO") in toinfwrd.tag.POS:
                        try:

                            if toinfwrd.normal_form == "я":
                                print("Ja", toinfwrd)
                                toinfwrd = morph.parse("ты")[0]
                                infwrd = toinfwrd.inflect({"accs", "2per"})
                            else:
                                infwrd = toinfwrd.inflect({userGender, toinfwrd.tag.POS, toinfwrd.tag.tense})
                            print(infwrd)
                            toins += "{} ".format(str(infwrd.word))
                        except:
                            print("err", wrd)
                            toins += "{} ".format(wrd)
                    else:
                        toins += "{} ".format(wrd)
                except:
                    toins += "{} ".format(wrd)
            replies = ["Определённо {} {}", "Точно {} {}", "Я уверен что {} {}"]
            if user['id'] == data['user_id']:
                args['message'] = "Ты {}".format(toins.replace("тебе", "себе"))
                bot.Replyqueue.put(args)
                return True
            if user['id'] == bot.MyUId:
                args['message'] = 'Определённо Я'
                bot.Replyqueue.put(args)
                return True
            name = '{} {}'.format(user['first_name'], user['last_name'])

            msg = random.choice(replies)
            args['message'] = msg.format(name, toins)
            # self.Reply(self.UserApi, args)
            bot.Replyqueue.put(args)


class Command_Prob:
    name = "вероятность"
    access = ["all"]
    desc = "Процент правдивости инфы"

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
    desc = "Говорит где что находится "

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        replies = ["Под столом", "На кровати", "За спиной", "На столе"]
        msg = random.choice(replies)
        args['message'] = msg
        # self.Reply(self.UserApi, args)
        bot.Replyqueue.put(args)


class Command_You:
    name = "ты!"
    access = ['all']
    desc = "Не обзывай бота"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        user = bot.GetUserNameById(data['user_id'])
        try:
            if user['sex'] == 2:
                replies = ["Сам ты {}", "Сам ты {}", "Сам ты {}", "Сам такой"]
            elif user['sex'] == 1:
                replies = ["Сама ты {}", "Сама ты {}", "Сама ты {}", "Сама такая"]
            else:
                replies = ["Само ты {}", "Само ты {}", "Само ты {}", "Само такое"]
        except:
            replies = ["Само ты {}", "Само ты {}", "Само ты {}", "Само такое"]
        msg = random.choice(replies)

        try:
            args['message'] = msg.format(" ".join(data['text'].split(' ')[1:]))
        except:
            args['message'] = msg
        # self.Reply(self.UserApi, args)
        bot.Replyqueue.put(args)


class Command_Help:
    name = "команды"
    access = ['all']
    desc = "Выводит это сообщение"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        a = ""
        for command in bot.Botmodules['commands'].keys():
            a += 'Команда: "{}", {}\n'.format(command, bot.Botmodules['commands'][command].desc)
        args['message'] = str(a)
        bot.Replyqueue.put(args)


class Command_resend:
    name = "перешли"
    access = ['all']
    desc = "Пересылает фото"

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
            att = bot.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        bot.Replyqueue.put(args)


class Command_kik:
    name = "изгнать"
    access = ['admin', 'moderator', 'editor']
    desc = "Изгоняет пользователя"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        user = data['custom']['id'] if 'id' in data['custom'] else None
        print(user)
        users = []
        for u in list([bot.UserGroups[user] for user in bot.UserGroups]):
            users.extend(u)
        print(users)
        if int(user) in users:
            args['message'] = "Нельзя кикать администрацию"
            bot.Replyqueue.put(args)
            return True
        name = bot.GetUserNameById(user)
        args['message'] = "The kickHammer has spoken\n {} has been kicked in the ass".format(
            ' '.join([name['first_name'], name['last_name']]))
        bot.UserApi.messages.removeChatUser(v=5.45, chat_id=data['peer_id'] - 2000000000, user_id=user)
        bot.Replyqueue.put(args)
        return True


class Command_JoinFiveNigths:
    name = "5nights"
    access = ["all"]
    desc = "Добавляет в беседу"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        are_friend = bot.UserApi.friends.areFriends(user_ids=[data['user_id']])[0]['friend_status']
        if int(are_friend) == 3:
            ans = bot.UserApi.messages.addChatUser(chat_id=13, user_id=data['user_id'])
            # ans = bot.UserApi.messages.addChatUser(chat_id=22, user_id=data['user_id'])

            if int(ans) != 1:
                args['message'] = 'Ошибка добавления'
            return True

        else:
            f = int(bot.UserApi.friends.add(user_id=data['user_id'], text='Что б добавить в беседу'))
            if f == 1 or f == 2:

                ans = bot.UserApi.messages.addChatUser(chat_id=13, user_id=data['user_id'])
                args['message'] = 'Примите завяку и снова напишите !5nights'
                if int(ans) != 1:
                    args['message'] = 'Ошибка добавления'

            else:
                args['message'] = 'Не могу добавить вас в друзья, а значит и не могу добавить в беседу'
            bot.Replyqueue.put(args)
            return True


class Command_ExecCode:
    name = "выполни"
    access = ['admin']
    desc = "Выполняет код из сообщения"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        code = bot.html_decode(data['message'])
        code = '\n'.join(code.split('<br>')[1:]).replace('|', '  ')
        a = compile(code, '<string>', 'exec')
        l = {'api': bot.UserApi, 'bot': bot}
        g = {}
        exec(a, g, l)
        args['message'] = str(l['out']) if 'out' in l else 'Выполнил'
        bot.Replyqueue.put(args)
        return True


class Command_StatComm:
    name = "инфо"
    access = ["all"]
    desc = "Статистика"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        msg = 'Кол-во обработанных сообщений: {}\nКол-во выполеных команд: {}\nРазмер кэша: {}\nКол-во живых потоков: {}\n'
        args['message'] = msg.format(bot.Stat['messages'], bot.Stat['commands'], str(
            prettier_size((os.path.getsize(os.path.join(getpath(), "../", 'tmp', 'cache.zip'))))),
                                     len([thread for thread in bot.EX_threadList if thread.isAlive()]))
        bot.Replyqueue.put(args)
        return True


class Command_AdminOnly:
    name = "дебаг"
    access = ["admin"]
    desc = "Врубает режим АдминОнли"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        bot.AdminModeOnly = not bot.AdminModeOnly
        msgOn = 'Включен режим дебага, принимаются сообщения только от админов'
        msgOff = 'Выключен режим дебага, принимаются все сообщения '
        args['message'] = msgOn if bot.AdminModeOnly else msgOff
        bot.Replyqueue.put(args)
        return True


class Command_BanAllGroupUsers:
    name = "забанитьнафигвсех"
    access = ["admin"]
    desc = "Банит всех участников группы к фигам"

    @staticmethod
    def execute(bot, data):
        exclude = 75615891
        ToBan = bot.GroupApi.groups.getMembers(group_id=data['custom']["id"])['items']
        if data['custom']["id"] == exclude:
            return
        args = {'v': "5.60", 'group_id': exclude}
        uid = int(data['custom']["id"])
        if "причина" in data['custom']:
            reason = int(args["причина"])
            args['reason'] = reason
        if "группа" in data['custom']:
            args['group_id'] = data['custom']["группа"]
        else:
            args['group_id'] = bot.Group.replace("-", "")
        args['user_id'] = uid
        if data['custom']["комментарий"]:
            comment = data['custom']["комментарий"]
            args['comment'] = comment
            args['comment_visible'] = 1

        if "время" in args:
            end_date = datetime.timestamp(datetime.now() + timedelta(hours=int(args["время"])))
            args["end_date"] = end_date
        for user in ToBan:
            args['user_id'] = user
            bot.GroupApi.groups.banUser(**args)


class Command_AddUser:
    name = "добавить"
    access = ["admin"]
    desc = "Устанавливает права на пользователя"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        print('Adduser: ', data)
        if "группа" in data['custom']:
            Group = data['custom']['группа'].lower()
        else:
            Group = "user"

        if 'id' in data['custom']:
            print(Group in bot.UserGroups)
            if Group in bot.UserGroups.keys():
                Ids = bot.UserGroups[Group]
                Ids.append(int(data['custom']['id']))
                bot.UserGroups[Group] = Ids
            else:
                bot.UserGroups[Group] = [int(data['custom']['id'])]

            userName = bot.GetUserNameById(data['custom']['id'])
            args['message'] = userName['first_name'] + ' ' + userName['last_name'] + ' был добавлен как ' + Group
            # self.Reply(self.UserApi, MArgs)
            bot.Replyqueue.put(args)
            bot.SaveConfig()


class Command_LockName:
    name = "namelock"
    access = ["admin"]
    desc = "Лочит имя беседы"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        id = str(data['peer_id'])
        if id in bot.Settings['namelock']:

            bot.Settings['namelock'][id] = [data['subject'], not data.Settings['namelock'][id][1]]

        else:
            bot.Settings['namelock'][id] = [data['subject'], True]
        if bot.Settings['namelock'][id][1]:
            args['message'] = 'Смена названия беседы запрещена'
            bot.Replyqueue.put(args)
        else:
            args['message'] = 'Смена названия беседы разрешена'
            bot.Replyqueue.put(args)
        bot.SaveConfig()
        return True


class Command_quit:
    name = "quit"
    access = ["admin"]
    desc = "Выключение бота"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id'],
                "message": "Увидимся позже"}
        bot.Replyqueue.put(args)
        sleep(2)
        os._exit(-9)


class Command_restart:
    name = "рестарт"
    access = ['admin']
    desc = "Рестарт бота"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60"}
        args['message'] = "Перезапуск всех потоков начат"
        bot.Replyqueue.put(args)
        with bot.Checkqueue.mutex:
            bot.Checkqueue.queue.clear()
        with bot.Longpool.mutex:
            bot.Longpool.queue.clear()
        sleep(3)
        # del bot.UserApi
        # del bot.GroupSession
        # del bot.UserSession
        # del bot.GroupApi

        bot.UserSession = SessionCapchaFix(access_token=bot.UserAccess_token)
        bot.GroupSession = SessionCapchaFix(access_token=bot.GroupAccess_token)
        bot.GroupApi = API(bot.GroupSession)
        bot.UserpApi = API(bot.UserSession)
        t = len(bot.LP_threads)
        for th in bot.LP_threads:
            try:
                th._stop()
                th.join()
                bot.LP_threads.pop(th)
            except:
                t -= 1
        for i in range(t):
            bot.LP_threads.append(threading.Thread(target=bot.parseLongPool))
            bot.LP_threads[i].setDaemon(True)
            bot.LP_threads[i].start()
        t = len(bot.EX_threadList)
        for th in bot.EX_threadList:
            try:
                th._stop()
                th.join()
                bot.EX_threadList.pop(th)
            except:
                t -= 1
        for i in range(t):
            bot.EX_threadList.append(threading.Thread(target=bot.ExecCommands))
            bot.EX_threadList[i].setDaemon(True)
            bot.EX_threadList[i].start()
        print("Чистим все ответы")
        with bot.Replyqueue.mutex:
            bot.Replyqueue.queue.clear()
        bot.ReplyThread._reset_internal_locks(False)
        bot.ReplyThread._stop()
        bot.ReplyThread.join()
        del bot.ReplyThread
        bot.ReplyThread = threading.Thread(target=bot.Reply)
        bot.ReplyThread.setDaemon(True)
        bot.ReplyThread.start()
        print("Перезапуск закончен")
        for name, val in globals().items():
            if isinstance(val, types.ModuleType):
                importlib.reload(val)
        args['message'] = "Перезапуск закончен"
        bot.Replyqueue.put(args)
        # os.system("RESTART.bat {}".format(os.getpid()))
        # #os.startfile(__file__,sys.executable)
        # #subprocess.Popen([sys.executable,__file__],close_fds=True,creationflags=0x00000008)
        # sleep(1)
        # #print(os.spawnv(os.P_NOWAIT, sys.executable, [__file__]))
        # os._exit(1)
        # #os.execv(__file__, sys.argv)


class Command_Zadolbali:
    name = "этослучилось"
    access = ["all"]
    desc = "Рандомная история с ithappens.me"

    class MLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.reset()
            self.fed = []

        def handle_data(self, d):
            self.fed.append(d)

        def get_data(self):
            return ''.join(self.fed)

    @staticmethod
    def strip_tags(html):
        s = Command_Zadolbali.MLStripper()
        s.feed(html)
        return s.get_data()

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        feed = feedparser.parse('http://www.ithappens.me/rss')['entries']
        zz = random.choice(feed)
        template = """      {}

         {}
          {}"""
        msg = template.format(zz['title'], Command_Zadolbali.strip_tags(zz['summary']), zz['link'])
        args['message'] = msg
        bot.Replyqueue.put(args)
        return True

        # if __name__ == "__main__":
        #    Command_Zadolbali().execute(None,{})


class Command_banCommand:
    name = "блок"
    access = ["admin", "editor", "moderator"]
    desc = "блокирует команду в чате"

    @staticmethod
    def execute(bot, data):
        comm = data['custom']['команда']
        if comm in ['bannedCommands']:
            bot.Settings['bannedCommands'][comm].append(str(data['peer_id']))
        else:
            bot.Settings['bannedCommands'][comm] = [str(data['peer_id'])]


class Command_Choice:
    name = "выбери"
    access = ["all"]
    desc = "Выбирает из представленных вариантов"

    @staticmethod
    def execute(bot, data):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        vars = " ".join(data['text']).split(',')
        var = random.choice(vars)
        templates = ['Я выбираю: {}', "Вот это: {}", "Думаю это лучший вариант: {}"]
        args['message'] = random.choice(templates).format(var)
        bot.Replyqueue.put(args)
