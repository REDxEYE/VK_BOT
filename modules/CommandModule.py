import json
import os
import random
import tempfile as tempF
import urllib
from datetime import datetime, timedelta
from html.parser import HTMLParser
from math import log
from time import sleep
from urllib.request import urlopen

try:
    import execjs

    execjsAvalible = True
except ImportError:
    execjsAvalible = False
    execjs = None
try:
    import feedparser

    feedparserAvalible = True
except ImportError:
    feedparser = None
    feedparserAvalible = False
try:
    import gtts

    gttsAvalable = True
except ImportError:
    gtts = None
    gttsAvalable = False
import pymorphy2
import requests
from libs.tempfile_ import TempFile
from utils import ArgBuilder

try:
    from .__Command_template import *
except ImportError:
    from __Command_template import *
from Module_manager_v2 import ModuleManager

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


def prettier_size(n, pow_=0, b=1024, u='B', pre=[''] + [p + 'i' for p in 'KMGTPEZY']):
    r, f = min(int(log(max(n * b ** pow_, 1), b)), len(pre) - 1), '{:,.%if} %s%s'
    return (f % (abs(r % (-r - 1)), pre[r], u)).format(n * b ** pow_ / b ** float(r))


@ModuleManager.command(names=["кого"], perm='text.whom', desc="Выбирает случайного человека")
class Command_Whom(C_template):
    name = ["кого"]
    access = ["all"]
    desc = "Выбирает случайного человека"
    perm = 'text.whom'
    cost = 2

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        text = data.message[:-1] if '?' in data.message else data.message
        if int(data.chat_id) <= 2000000000:
            args.message = "Тебя"
            return args
        else:
            toinf = text.split(" ")
            toins = ""
            ud = LongPoolUpdates.GetUserProfile(random.choice(data.chat_active))
            if ud.sex == 2:
                userGender = "masc"
            elif ud.sex == 1:
                userGender = "femn"
            else:
                userGender = "neut"
            for wrd in toinf:
                print(wrd)
                toinfwrd = morph.parse(wrd)[0]
                if ('VERB' in toinfwrd.tag.POS) or ("NPRO" in toinfwrd.tag.POS):
                    try:

                        if toinfwrd.normal_form == "я":
                            print("Ja", toinfwrd)
                            toinfwrd = morph.parse("ты")[0]
                            infwrd = toinfwrd.inflect({"accs", "2per"})
                        else:
                            infwrd = toinfwrd.inflect({userGender, toinfwrd.tag.POS})
                        print(infwrd)
                        toins += "{} ".format(str(infwrd.word))
                    except Exception:
                        print("err", wrd)
                else:
                    toins += "{} ".format(wrd)

            if ud.id == self.api.MyUId:
                args.message = 'Определённо меня'
                self.api.Replyqueue.put(args)
            name = '*id{} ({} {})'.format(str(ud.id), ud.first_name_acc, ud.last_name_acc)
            replies = ["Определённо {}", "Точно {}", "Я уверен что его -  {}"]
            msg = random.choice(replies)
            args.message = msg.format(name)
            # self.Reply(self.UserApi, args)
            self.api.Replyqueue.put(args.AsDict_())


@ModuleManager.command(names=["кто?"], perm='text.who', desc="Выбирает случайного человека", cost=2)
class Command_Who(C_template):
    name = ["кто?"]
    access = ["all"]
    desc = "Выбирает случайного человека"
    perm = 'text.who'
    cost = 2

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        text = data.text[:-1] if data.text.endswith('?') else data.text
        text = text.replace('мне', 'тебе')
        text = text.replace('мной', 'тобой')
        text = text.replace('моей', 'твоей')
        text = text.replace('меня', 'тебя')
        if not data.isChat:
            args['message'] = "Ты"
            self.api.Replyqueue.put(args)
            return True
        else:
            ud = self.api.GetUserNameById(random.choice(data.chat_active))

            if ud.sex == 2:
                userGender = "masc"
            elif ud.sex == 1:
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

                            infwrd = toinfwrd.inflect({userGender, toinfwrd.tag.POS, toinfwrd.tag.tense})
                            print(infwrd)
                            toins += f"{str(infwrd.word)} "
                        except:
                            print("err", wrd)
                            toins += "{} ".format(wrd)
                    else:
                        toins += "{} ".format(wrd)
                except:
                    toins += "{} ".format(wrd)
            replies = ["Определённо {} {}", "Точно {} {}", "Я уверен что {} {}"]
            if ud.id == data.user_id:
                args.message = "Ты {}".format(toins.replace("тебе", "себе"))
                self.api.Replyqueue.put(args)
                return True
            if ud.id == self.api.MyUId:
                args.message = 'Определённо Я'
                self.api.Replyqueue.put(args)
                return True
            name = '*id{} ({} {})'.format(str(ud.id), ud.first_name_nom, ud.last_name_nom)

            msg = random.choice(replies)
            args.message = msg.format(name, toins)
            # self.Reply(self.UserApi, args)
            self.api.Replyqueue.put(args)


@ModuleManager.command(names=["вероятность"], perm='text.prob', desc="Процент правдивости инфы")
class Command_Prob(C_template):
    name = ["вероятность"]
    access = ["all"]
    desc = "Процент правдивости инфы"
    perm = 'text.prob'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        a = data.body.split(' ')
        if 'вероятность' in a[1]:
            a = a[2:]
        else:
            a = a[1:]
        msg = "Вероятность того, что {}, равна {}%".format(' '.join(a), random.randint(0, 100))
        args['message'] = msg
        # self.Reply(self.UserApi, args)
        self.api.Replyqueue.put(args)


@ModuleManager.command(names=["где"], desc='Говорит где что находится', perm='text.where')
class Command_Where(C_template):
    name = ["где"]
    access = ["all"]
    desc = "Говорит где что находится "
    perm = 'text.where'
    cost = 2

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)

        replies = ["Под столом", "На кровати", "За спиной", "На столе"]
        msg = random.choice(replies)
        args['message'] = msg
        # self.Reply(self.UserApi, args)
        self.api.Replyqueue.put(args)


@ModuleManager.command(names=["ты!"], desc='Не обзывай бота', perm='text.you', template="{botname}, ты!")
class Command_You(C_template):
    name = ["ты!"]
    access = ['all']
    desc = "Не обзывай бота"
    template = "{botname}, ты!"
    perm = 'text.you'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setforward_messages(data.id).setpeer_id(data.chat_id)

        usr = LongPoolUpdates.GetUserProfile(data.user_id)
        try:
            if usr.sex == 2:
                replies = ["Сам ты {}", "Сам ты {}", "Сам ты {}", "Сам такой"]
            elif usr.sex == 1:
                replies = ["Сама ты {}", "Сама ты {}", "Сама ты {}", "Сама такая"]
            else:
                replies = ["Само ты {}", "Само ты {}", "Само ты {}", "Само такое"]
        except:
            replies = ["Само ты {}", "Само ты {}", "Само ты {}", "Само такое"]
        msg = random.choice(replies)

        try:
            args['message'] = msg.format(' '.join(data.text.split(' ')))
        except:
            args['message'] = msg
        # self.Reply(self.UserApi, args)
        self.api.Replyqueue.put(args)
        return True


@ModuleManager.command(names=["команды", "помощь"], desc="Выводит это сообщение", perm='text.help',
                       template='"{botname}, помощь" или "{botname}, команды" - выводится список команд,\nа "{botname}, помощь НАЗВАНИЕ КОМАНДЫ" или "{botname}, команды НАЗВАНИЕ_КОМАНДЫ" - Выведет шаблон запроса')
class Command_Help(C_template):
    name = ["команды", "помощь"]
    access = ['all']
    desc = "Выводит это сообщение"
    template = '"{botname}, помощь" или "{botname}, команды" - выводится список команд,\nа "{botname}, помощь НАЗВАНИЕ КОМАНДЫ" или "{botname}, команды НАЗВАНИЕ_КОМАНДЫ" - Выведет шаблон запроса'
    perm = 'text.help'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        if len(data.args) >= 1 and data.args[0] != "":
            print(data.args)
            Command_Help.GetHelp(data, data.args[0])
            return
        args['message'] = 'Список команд'
        a = "Вам доступны:\n"
        UserPerms = self.api.USERS.GetPerms(data.user_id)
        for command in self.api.MODULES.GetAvailable(UserPerms):
            a += 'Команда: "{}", {}. Стоимость: {}\n'.format('" или "'.join(command.names), command.desc, command.cost)
        args['message'] = str(a)
        self.api.Replyqueue.put(args)
        return True

    def GetHelp(self, data: LongPoolHistoryMessage, command):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)

        if self.api.MODULES.isValid(command):
            mod = self.api.MODULES.GetModule(command)
            try:
                args['message'] = mod.template.format(botname=self.api.MyName.first_name)
            except:
                args['message'] = mod.template.format(botname="Имя бота")

        else:
            args['message'] = 'Неизвестная команда'
        self.api.Replyqueue.put(args)


@ModuleManager.command(names=["перешли"], desc="Пересылает фото", perm='text.resend', template="{botname}, перешли")
class Command_resend(C_template):
    name = ["перешли"]
    access = ['all']
    desc = "Пересылает фото"
    template = "{botname}, перешли"
    perm = 'text.resend'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)

        Topost = []
        for att in data.attachments:
            try:

                photo = att.photo.GetHiRes
            except:
                return 'Error'

            req = urllib.request.Request(photo, headers=HDR)

            img = urlopen(req).read()

            Tmp = TempFile(img, 'jpg')
            att = self.api.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        self.api.Replyqueue.put(args)
        return True


@ModuleManager.command(names=["изгнать", "kick", "votekick"], desc="Изгоняет пользователя", perm='chat.kick',
                       template="{botname}, изгнать UID1 UID2 UID3")
class Command_kick(C_template):
    name = ["изгнать", "kick", "votekick"]
    access = ['admin', 'moderator', 'editor']
    desc = "Изгоняет пользователя"
    template = "{botname}, изгнать UID1 UID2 UID3"
    perm = 'chat.kick'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        ToKick = list(data.custom['id']) if 'id' in data.custom else data.text.split(' ')
        if len(ToKick) < 1:
            return False

        for user in ToKick:
            if self.api.USERS.GetStatus(data.user_id) in ['admin', 'moder']:
                args['message'] = "Нельзя кикать администрацию"
                self.api.Replyqueue.put(args)
                continue
            name = LongPoolUpdates.GetUserProfile(data.user_id)
            args['message'] = "The kickHammer has spoken\n {} has been kicked in the ass".format(
                ' '.join([name.first_name, name.last_name]))
            print(data)
            self.api.UserApi.messages.removeChatUser(v=5.45, chat_id=data.chat_id - 2000000000, user_id=user)
            self.api.Replyqueue.put(args)
        return True


#@ModuleManager.command(names=["5nights"], desc="Добавляет в беседу", perm='text.joinChat',
#                       template="{botname}, 5nights")
class Command_JoinFiveNigths(C_template):
    name = ["5nights"]
    access = ["all"]
    desc = "Добавляет в беседу"
    perm = 'text.joinChat'
    template = '{botname}, 5nights'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)

        are_friend = self.api.UserApi.friends.areFriends(user_ids=[data.user_id])[0]['friend_status']
        if int(are_friend) == 3:
            ans = self.api.UserApi.messages.addChatUser(chat_id=13, user_id=data.user_id)
            # ans = self.api.UserApi.messages.addChatUser(chat_id=22, user_id=data.user_id)

            if int(ans) != 1:
                args['message'] = 'Ошибка добавления'
            return True

        else:
            f = int(self.api.UserApi.friends.add(user_id=data.user_id, text='Что б добавить в беседу'))
            if f == 1 or f == 2:

                ans = self.api.UserApi.messages.addChatUser(chat_id=13, user_id=data.user_id)
                args['message'] = 'Примите завяку и снова напишите !5nights'
                if int(ans) != 1:
                    args['message'] = 'Ошибка добавления'

            else:
                args['message'] = 'Не могу добавить вас в друзья, а значит и не могу добавить в беседу'
            self.api.Replyqueue.put(args)
            return True


@ModuleManager.command(names=["инфо", "инфа", "info", 'stats', 'stat'], desc="Статистика", perm='text.info',
                       template='{botname}, инфо')
class Command_StatComm(C_template):
    name = ["инфо", "инфа", "info", 'stats', 'stat']
    access = ["all"]
    desc = "Статистика"
    perm = 'text.info'
    template = '{botname}, инфо'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)

        msg = 'Кол-во обработанных сообщений: {}\nКол-во выполеных команд: {}\nЗарегестрировано польхователей: {}\nРазмер кэша: {}\nКол-во живых потоков: {}\n'
        args['message'] = msg.format(self.api.Stat['messages'], self.api.Stat['commands'], len(self.api.USERS.DB),
                                     self.api.Stat['cache'],
                                     len([thread for thread in self.api.EX_threadList if thread.is_alive()]))
        self.api.Replyqueue.put(args)
        return True


@ModuleManager.command(names=["дебаг"], desc="Врубает режим АдминОнли", perm='core.debug', template='{botname}, дебаг')
class Command_AdminOnly(C_template):
    name = ["дебаг"]
    access = ["admin"]
    desc = "Врубает режим АдминОнли"
    perm = 'core.debug'
    template = '{botname}, дебаг'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)

        self.api.AdminModeOnly = not self.api.AdminModeOnly
        msgOn = 'Включен режим дебага, принимаются сообщения только от админов'
        msgOff = 'Выключен режим дебага, принимаются все сообщения '
        args['message'] = msgOn if self.api.AdminModeOnly else msgOff
        self.api.Replyqueue.put(args)
        return True


# @ModuleManager.command(names=["забанитьнафигвсех"], desc="Банит всех участников группы к фигам", perm='core.banNahoi', template='{botname}, забанитьнафигвсех\n' \
#               'причина:цифра\n' \
#               'группа:ИД группы\n' \
#               'комантарий:Ваш комент\n' \
#               'время:срок в часах')
class _Command_BanAllGroupUsers(C_template):
    name = ["забанитьнафигвсех"]
    access = ["admin"]
    desc = "Банит всех участников группы к фигам"
    perm = 'core.banNahoi'
    template = '{botname}, забанитьнафигвсех\n' \
               'причина:цифра\n' \
               'группа:ИД группы\n' \
               'комантарий:Ваш комент\n' \
               'время:срок в часах'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        exclude = 75615891
        ToBan = self.api.GroupApi.groups.getMembers(group_id=data.custom["id"], count=1000)['items']
        if data.custom["id"] == exclude:
            return
        args = {'v': "5.60", 'group_id': exclude}

        if "причина" in data.custom:
            reason = int(args["причина"])
            args['reason'] = reason
        if "группа" in data.custom:
            args['group_id'] = data.custom["группа"]
        else:
            args['group_id'] = self.api.Group.replace("-", "")
        if data.custom["комментарий"]:
            comment = data.custom["комментарий"]
            args['comment'] = comment
            args['comment_visible'] = 1

        if "время" in args:
            end_date = datetime.timestamp(datetime.now() + timedelta(hours=int(args["время"])))
            args["end_date"] = end_date
        for user in ToBan:
            args['user_id'] = user
            self.api.GroupApi.groups.banUser(**args)
            sleep(1)


@ModuleManager.command(names=['about', 'ктоты'], desc='Выводит информацию о боте', perm='text.about',
                       template='{botname}, about')
class Command_About(C_template):
    name = ['about', 'ктоты']
    access = ['all']
    desc = 'Выводит информацию о боте'
    perm = 'text.about'
    template = '{botname}, about'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)

        args['message'] = \
            'Создан *red_eye_rus (Red Dragon)\n' \
            'Множество идей взяты у *rukifox (Яна)\n' \
            #'GitHub: www.github.com/REDxEYE/VK_BOT\n'
        self.api.Replyqueue.put(args)

#@ModuleManager.command(names=["namelock"], desc="Лочит имя беседы", perm='chat.LockName',template='{botname}, namelock')
class Command_LockName(C_template):
    name = ["namelock"]
    access = ["admin"]
    desc = "Лочит имя беседы"
    perm = 'chat.LockName'
    template = '{botname}, namelock'


    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        id = int(data.id)
        if id not in self.api.Settings['namelock']:
            args['message'] = 'Смена названия беседы запрещена'
            self.api.Replyqueue.put(args)
            self.api.Settings['namelock'].append(id)

        else:

            self.api.Settings['namelock'].remove(id)
            args['message'] = 'Смена названия беседы разрешена'
            self.api.Replyqueue.put(args)
        self.api.SaveConfig()
        return True

@ModuleManager.command(names=["этослучилось", 'ithappens'], desc="Рандомная история с ithappens.me", perm='text.Zadolbali',template= '{botname}, этослучилось')
class Command_ithappens(C_template):
    name = ["этослучилось", 'ithappens']
    access = ["all"]
    desc = "Рандомная история с ithappens.me"
    perm = 'text.Zadolbali'
    template = '{botname}, этослучилось'

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
        s = Command_ithappens.MLStripper()
        s.feed(html)
        return s.get_data()

    
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        feed = feedparser.parse('http://www.ithappens.me/rss')['entries']
        zz = random.choice(feed)
        template = """      {}

         {}
          {}"""
        msg = template.format(zz['title'], Command_ithappens.strip_tags(zz['summary']), zz['link'])
        args['message'] = msg
        self.api.Replyqueue.put(args)
        return True

        # if __name__ == "__main__":
        #    Command_Zadolbali().execute(None,{})

@ModuleManager.command(names=["блок"], desc="блокирует команду в чате", perm='chat.BlockCommand', template='{botname}, блок\n' \
               'команда:название команды\n')
class Command_banCommand(C_template):
    name = ["блок"]
    access = ["admin", "editor", "moderator"]
    desc = "блокирует команду в чате"
    perm = 'chat.BlockCommand'
    template = '{botname}, блок\n' \
               'команда:название команды\n'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        comm = data.custom['команда']
        if comm in ['bannedCommands']:
            self.api.Settings['bannedCommands'][comm].append(str(data.id))
        else:
            self.api.Settings['bannedCommands'][comm] = [str(data.id)]

@ModuleManager.command(names= ["выбери"], desc="Выбирает из представленных вариантов", perm='text.choice', template='{botname}, вариант1 вариант2 вариант3 вариантN ')
class Command_Choice(C_template):
    name = ["выбери"]
    access = ["all"]
    desc = "Выбирает из представленных вариантов"
    perm = 'text.choice'
    template = '{botname}, вариант1 вариант2 вариант3 вариантN '

    @staticmethod
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        var = random.choice(data.args)
        templates = ['Я выбираю: {}', "Вот это: {}", "Думаю это лучший вариант: {}"]
        args['message'] = random.choice(templates).format(var)
        self.api.Replyqueue.put(args)

@ModuleManager.command(names= ["скажи"], desc='Произносит ваш текст на выбранном языке ("Имя бота", "нужный язык (2буквы)" " ВАШ ТЕКСТ")', perm='text.tts', template='{botname}, нужный язык(2буквы) ВАШ ТЕКСТ)')
class Command_TTS(C_template):
    enabled = gttsAvalable
    name = ["скажи"]
    access = ['all']
    desc = 'Произносит ваш текст на выбранном языке ("Имя бота", "нужный язык (2буквы)" " ВАШ ТЕКСТ")'
    perm = 'text.tts'
    template = '{botname}, нужный язык(2буквы) ВАШ ТЕКСТ)'


    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        apiurl = f"https://api.vk.com/method/docs.getUploadServer?access_token={self.api.UserAccess_token}&type=audio_message&v=5.60"
        server = json.loads(urlopen(apiurl).read().decode('utf-8'))['response']['upload_url']
        for i in Command_TTS.name:
            if i in data.body:
                text = data.body.replace('<br>', '').split(i)[-1].split(" ")[1:]
        # text = data.text.split(' ')
        lang = text[0]
        if lang not in gtts.gTTS.LANGUAGES:
            lang = 'ru'

        tts = gtts.gTTS(' '.join(text[1:]), lang=lang, debug=True)
        a = tempF.NamedTemporaryFile('w+b', suffix='.mp3', dir='tmp', delete=False)
        try:
            tts.write_to_fp(a)
        except:
            args['message'] = 'Технические сложности. Обратитесь через пару секунд'
            self.api.Replyqueue.put(args)
            return
        a.close()
        req = requests.post(server, files={'file': open(a.name, 'rb')})
        os.remove(a.name)
        if req.status_code == requests.codes.ok:
            print('req', req.json())
            params = {'file': req.json()['file'], 'v': '5.60'}
            doc = self.api.UserApi.docs.save(**params)[0]

            Voice = 'doc{}_{}'.format(doc['owner_id'], doc['id'])
            args['attachment'] = Voice
            self.api.Replyqueue.put(args)




@ModuleManager.command(names= ['зашквар', "жир"], desc='Замеряет зашкварность сообщения', perm='text.zashkvar', template='{botname}, зашквар')
class Command_Zashkvar(C_template):
    name = ['зашквар', "жир"]
    access = ['user']
    desc = 'Замеряет зашкварность сообщения'
    perm = 'text.zashkvar'
    template = '{botname}, зашквар'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        if len(data.fwd_messages) > 0:
            try:
                message = data.fwd_messages[0]
                try:
                    temp = len(message.body)
                except:
                    temp = message.date
            except:
                args['message'] = "Непонятная ошибочка."
                self.api.Replyqueue.put(args)
                return

            print(temp)
            random.seed(temp)
            zh = random.randint(0, 100)
            template = "Зашкварность - {}%"
            args['message'] = template.format(zh)
            self.api.Replyqueue.put(args)


        else:
            args['message'] = "Нечего мерять. Прикрепи к команде сообшение, зашкварность которого хочешь померять"
            self.api.Replyqueue.put(args)
