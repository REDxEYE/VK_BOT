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

from DataTypes.group import group,contacts_group
from utils import ArgBuilder
try:
    import execjs

    execjsAvalible = True
except:
    execjsAvalible = False
    execjs = None
try:
    import feedparser

    feedparserAvalible = True
except:
    feedparser = None
    feedparserAvalible = False
try:
    import gtts
    gttsAvalable = True
except:
    gtts = None
    gttsAvalable = False
import pymorphy2
import requests
from libs import VK_foaf
from libs.tempfile_ import TempFile
from DataTypes.contacts import contacts
from utils import ArgBuilder
try:
    from .__Command_template import *
except:
    from __Command_template import *

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


class Command_Whom(C_template):
    name = ["кого"]
    access = ["all"]
    desc = "Выбирает случайного человека"
    perm = 'text.whom'
    cost = 2

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        text = " ".join(data.body.split(',')[1].split(' ')[2:]) if "?" not in data.body else " ".join(
            data.body.split(',')[1].split(' ')[2:])[:-1]
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

            if ud.id == bot.MyUId:
                args.message = 'Определённо меня'
                bot.Replyqueue.put(args)
            name = '*id{} ({} {})'.format(str(ud.id), ud.first_name_acc, ud.last_name_acc)
            replies = ["Определённо {}", "Точно {}", "Я уверен что его -  {}"]
            msg = random.choice(replies)
            args.message = msg.format(name)
            # self.Reply(self.UserApi, args)
            bot.Replyqueue.put(args.AsDict_())


class Command_Who(C_template):
    name = ["кто?"]
    access = ["all"]
    desc = "Выбирает случайного человека"
    perm = 'text.who'
    cost = 2

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True) -> bool:
        """

        Args:
            forward (bool):
            LongPoolUpdates (Updates):
            data (LongPoolMessage):
            bot (Vk_bot2.bot):
        """

        args = {"peer_id": data.chat_id, "v": "5.60", }

        if forward:
            args.update({"forward_messages": data.id})
        text = " ".join(
            data.body.split(',')[1].split(' ')[2:])[:-1] if data.body.endswith("?") else " ".join(
            data.body.split(',')[1].split(' ')[2:])
        if "мне" in text: text = text.replace('мне', 'тебе')
        if "мной" in text: text = text.replace('мной', 'тобой')
        if "моей" in text: text = text.replace('моей', 'твоей')
        if not data.isChat:
            args['message'] = "Ты"
            bot.Replyqueue.put(args)
            return True
        else:
            ud = bot.GetUserNameById(random.choice(data.chat_active))
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
            if ud.id == data.user_id:
                args['message'] = "Ты {}".format(toins.replace("тебе", "себе"))
                bot.Replyqueue.put(args)
                return True
            if ud.id == bot.MyUId:
                args['message'] = 'Определённо Я'
                bot.Replyqueue.put(args)
                return True
            name = '*id{} ({} {})'.format(str(ud.id), ud.first_name_nom, ud.last_name_nom)

            msg = random.choice(replies)
            args['message'] = msg.format(name, toins)
            # self.Reply(self.UserApi, args)
            bot.Replyqueue.put(args)


class Command_Prob(C_template):
    name = ["вероятность"]
    access = ["all"]
    desc = "Процент правдивости инфы"
    perm = 'text.prob'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        a = data.body.split(' ')
        if 'вероятность' in a[1]:
            a = a[2:]
        else:
            a = a[1:]
        msg = "Вероятность того, что {}, равна {}%".format(' '.join(a), random.randint(0, 100))
        args['message'] = msg
        # self.Reply(self.UserApi, args)
        bot.Replyqueue.put(args)


class Command_Where(C_template):
    name = ["где"]
    access = ["all"]
    desc = "Говорит где что находится "
    perm = 'text.where'
    cost = 2

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        replies = ["Под столом", "На кровати", "За спиной", "На столе"]
        msg = random.choice(replies)
        args['message'] = msg
        # self.Reply(self.UserApi, args)
        bot.Replyqueue.put(args)


class Command_You(C_template):
    name = ["ты!"]
    access = ['all']
    desc = "Не обзывай бота"
    template = "{botname}, ты!"
    perm = 'text.you'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
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
        bot.Replyqueue.put(args)
        return True


class Command_Help(C_template):
    name = ["команды", "помощь"]
    access = ['all']
    desc = "Выводит это сообщение"
    template = '"{botname}, помощь" или "{botname}, команды" - выводится список команд,\nа "{botname}, помощь НАЗВАНИЕ КОМАНДЫ" или "{botname}, команды НАЗВАНИЕ_КОМАНДЫ" - Выведет шаблон запроса'
    perm = 'text.help'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        if len(data.args) >= 1 and data.args[0] != "":
            print(data.args)
            Command_Help.GetHelp(bot, data, data.args[0], forward)
            return
        args['message'] = 'Список команд'
        a = "Вам доступны:\n"
        UserPerms = bot.USERS.GetPerms(data.user_id)
        for command in bot.MODULES.GetAvailable(UserPerms):
            a += 'Команда: "{}", {}. Стоимость: {}\n'.format('" или "'.join(command.names), command.desc, command.cost)
        args['message'] = str(a)
        bot.Replyqueue.put(args)
        return True

    @staticmethod
    def GetHelp(bot: Vk_bot2.Bot, data:LongPoolMessage, command, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        if bot.MODULES.isValid(command):
            mod = bot.MODULES.GetModule(command)
            try:
                args['message'] = mod.template.format(botname=bot.MyName.first_name)
            except:
                args['message'] = mod.template.format(botname="Имя бота")

        else:
            args['message'] = 'Неизвестная команда'
            bot.Replyqueue.put(args)
            return
        bot.Replyqueue.put(args)


class Command_resend(C_template):
    name = ["перешли"]
    access = ['all']
    desc = "Пересылает фото"
    template = "{botname}, перешли"
    perm = 'text.resend'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})

        Topost = []
        for att in data.attachments:
            try:

                photo = att.photo
            except:
                return 'Error'

            req = urllib.request.Request(photo, headers=HDR)

            img = urlopen(req).read()

            Tmp = TempFile(img, 'jpg')
            att = bot.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        bot.Replyqueue.put(args)
        return True


class Command_kick(C_template):
    name = ["изгнать", "kick", "votekick"]
    access = ['admin', 'moderator', 'editor']
    desc = "Изгоняет пользователя"
    template = "{botname}, изгнать UID1 UID2 UID3"
    perm = 'chat.kick'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        ToKick = list(data.custom['id']) if 'id' in data.custom else data.text.split(' ')
        if len(ToKick) < 1:
            return False

        for user in ToKick:
            if bot.USERS.GetStatus(data.user_id) in ['admin', 'moder']:
                args['message'] = "Нельзя кикать администрацию"
                bot.Replyqueue.put(args)
                continue
            name = LongPoolUpdates.GetUserProfile(data.user_id)
            args['message'] = "The kickHammer has spoken\n {} has been kicked in the ass".format(
                ' '.join([name.first_name, name.last_name]))
            print(data)
            bot.UserApi.messages.removeChatUser(v=5.45, chat_id=data.chat_id - 2000000000, user_id=user)
            bot.Replyqueue.put(args)
        return True


class Command_JoinFiveNigths(C_template):
    name = ["5nights"]
    access = ["all"]
    desc = "Добавляет в беседу"
    perm = 'text.joinChat'
    template = '{botname}, 5nights'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        are_friend = bot.UserApi.friends.areFriends(user_ids=[data.user_id])[0]['friend_status']
        if int(are_friend) == 3:
            ans = bot.UserApi.messages.addChatUser(chat_id=13, user_id=data.user_id)
            # ans = bot.UserApi.messages.addChatUser(chat_id=22, user_id=data.user_id)

            if int(ans) != 1:
                args['message'] = 'Ошибка добавления'
            return True

        else:
            f = int(bot.UserApi.friends.add(user_id=data.user_id, text='Что б добавить в беседу'))
            if f == 1 or f == 2:

                ans = bot.UserApi.messages.addChatUser(chat_id=13, user_id=data.user_id)
                args['message'] = 'Примите завяку и снова напишите !5nights'
                if int(ans) != 1:
                    args['message'] = 'Ошибка добавления'

            else:
                args['message'] = 'Не могу добавить вас в друзья, а значит и не могу добавить в беседу'
            bot.Replyqueue.put(args)
            return True





class Command_StatComm(C_template):
    name = ["инфо", "инфа", "info", 'stats', 'stat']
    access = ["all"]
    desc = "Статистика"
    perm = 'text.info'
    template = '{botname}, инфо'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        msg = 'Кол-во обработанных сообщений: {}\nКол-во выполеных команд: {}\nЗарегестрировано польхователей: {}\nРазмер кэша: {}\nКол-во живых потоков: {}\n'
        args['message'] = msg.format(bot.Stat['messages'], bot.Stat['commands'], len(bot.USERS.DB), bot.Stat['cache'],
                                     len([thread for thread in bot.EX_threadList if thread.is_alive()]))
        bot.Replyqueue.put(args)
        return True


class Command_AdminOnly(C_template):
    name = ["дебаг"]
    access = ["admin"]
    desc = "Врубает режим АдминОнли"
    perm = 'core.debug'
    template = '{botname}, дебаг'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        bot.AdminModeOnly = not bot.AdminModeOnly
        msgOn = 'Включен режим дебага, принимаются сообщения только от админов'
        msgOff = 'Выключен режим дебага, принимаются все сообщения '
        args['message'] = msgOn if bot.AdminModeOnly else msgOff
        bot.Replyqueue.put(args)
        return True


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

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        exclude = 75615891
        ToBan = bot.GroupApi.groups.getMembers(group_id=data.custom["id"], count=1000)['items']
        if data.custom["id"] == exclude:
            return
        args = {'v': "5.60", 'group_id': exclude}

        if "причина" in data.custom:
            reason = int(args["причина"])
            args['reason'] = reason
        if "группа" in data.custom:
            args['group_id'] = data.custom["группа"]
        else:
            args['group_id'] = bot.Group.replace("-", "")
        if data.custom["комментарий"]:
            comment = data.custom["комментарий"]
            args['comment'] = comment
            args['comment_visible'] = 1

        if "время" in args:
            end_date = datetime.timestamp(datetime.now() + timedelta(hours=int(args["время"])))
            args["end_date"] = end_date
        for user in ToBan:
            args['user_id'] = user
            bot.GroupApi.groups.banUser(**args)
            sleep(1)


class Command_About(C_template):
    name = ['about', 'ктоты']
    access = ['all']
    desc = 'Выводит информацию о боте'
    perm = 'text.about'
    template = '{botname}, about'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})

        args['message'] = \
            'Создан *red_eye_rus (Red Dragon)\n' \
            'Множество идей взяты у *rukifox (Яна)\n' \
            'GitHub: www.github.com/REDxEYE/VK_BOT\n'
        bot.Replyqueue.put(args)


class Command_LockName(C_template):
    name = ["namelock"]
    access = ["admin"]
    desc = "Лочит имя беседы"
    perm = 'chat.LockName'
    template = '{botname}, namelock'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        id = int(data.id)
        if id not in bot.Settings['namelock']:
            args['message'] = 'Смена названия беседы запрещена'
            bot.Replyqueue.put(args)
            bot.Settings['namelock'].append(id)

        else:

            bot.Settings['namelock'].remove(id)
            args['message'] = 'Смена названия беседы разрешена'
            bot.Replyqueue.put(args)
        bot.SaveConfig()
        return True



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

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        feed = feedparser.parse('http://www.ithappens.me/rss')['entries']
        zz = random.choice(feed)
        template = """      {}

         {}
          {}"""
        msg = template.format(zz['title'], Command_ithappens.strip_tags(zz['summary']), zz['link'])
        args['message'] = msg
        bot.Replyqueue.put(args)
        return True

        # if __name__ == "__main__":
        #    Command_Zadolbali().execute(None,{})


class Command_banCommand(C_template):
    name = ["блок"]
    access = ["admin", "editor", "moderator"]
    desc = "блокирует команду в чате"
    perm = 'chat.BlockCommand'
    template = '{}, блок\n' \
               'команда:название команды\n'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        comm = data.custom['команда']
        if comm in ['bannedCommands']:
            bot.Settings['bannedCommands'][comm].append(str(data.id))
        else:
            bot.Settings['bannedCommands'][comm] = [str(data.id)]


class Command_Choice(C_template):
    name = ["выбери"]
    access = ["all"]
    desc = "Выбирает из представленных вариантов"
    perm = 'text.choice'
    template = '{botname}, вариант1 вариант2 вариант3 вариантN '

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        vars = data.text.split(' ')
        var = random.choice(vars)
        templates = ['Я выбираю: {}', "Вот это: {}", "Думаю это лучший вариант: {}"]
        args['message'] = random.choice(templates).format(var)
        bot.Replyqueue.put(args)





# import lupa
# from lupa import LuaRuntime
# lua = LuaRuntime(unpack_returned_tuples=True)
# class Command_Lua(Command_template):
#    name = 'Lua'
#    access = ['admin']
#    desc = 'Выполняет JS скрипт'
#    @staticmethod
#    def execute(bot:Vk_bot2.bot,data):
#        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
#        code = bot.html_decode(' '.join(data.body.split('<br>')[1:]))
#        l = lua.eval(code)
#        args['message'] = l
#        bot.Replyqueue.put(args)
class Command_TTS(C_template):
    enabled = gttsAvalable
    name = ["скажи"]
    access = ['all']
    desc = 'Произносит ваш текст на выбранном языке ("Имя бота", "нужный язык (2буквы)" " ВАШ ТЕКСТ")'
    perm = 'text.tts'
    template = '{botname}, нужный язык(2буквы) ВАШ ТЕКСТ)'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        apiurl = 'https://api.vk.com/method/docs.getUploadServer?access_token={}&type=audio_message&v=5.60'.format(
            bot.UserAccess_token)
        print(apiurl)
        server = json.loads(urlopen(apiurl).read().decode('utf-8'))['response']['upload_url']
        print(server)
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
            bot.Replyqueue.put(args)
            return
        a.close()
        req = requests.post(server, files={'file': open(a.name, 'rb')})
        os.remove(a.name)
        if req.status_code == requests.codes.ok:
            print('req', req.json())
            params = {'file': req.json()['file'], 'v': '5.60'}
            doc = bot.UserApi.docs.save(**params)[0]

            Voice = 'doc{}_{}'.format(doc['owner_id'], doc['id'])
            args['attachment'] = Voice
            bot.Replyqueue.put(args)


#class _Command_RemoteExec(C_template):
#    name = ["безпалева"]
#    access = ['admin']
#    desc = "Выполняет команду в лс/беседе другого человека"
#    perm = 'core.remoteExec'
#
#    @staticmethod
#    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
#        RemoteData = copy.deepcopy(data)
#        args = {"peer_id": data.chat_id, "v": "5.60"}
#        CustomArgs = data.custom
#        if ('peer_id' not in CustomArgs) or ('command' not in CustomArgs):
#            return False
#        for t in data.custom:
#            RemoteData.update({t: data.custom[t]})
#        if int(CustomArgs['peer_id']) < 2000000000:
#            try:
#                print(CustomArgs['peer_id'])
#                a = bot.UserApi.messages.getChat(chat_id=int(CustomArgs['peer_id']))
#                RemoteData.update({'peer_id': int(CustomArgs['peer_id']) + 2000000000})
#            except Exception as E:
#                print(E)
#                bot.Replyqueue.put(
#                    {"peer_id": data.chat_id, "v": "5.60", 'message': 'Другим людям в личку нельзя писать'})
#                return 'error'
#        chat = bot.UserApi.messages.getChat(
#            chat_id=int(CustomArgs['peer_id']) if int(CustomArgs['peer_id']) < 2000000000 else int(
#                CustomArgs['peer_id']) - 2000000000)['title']
#        args['message'] = "Нужная беседа - {}?".format(chat)
#        bot.Replyqueue.put(args)
#        ans = bot.WaitForMSG(3, data)
#        print(ans)
#        if re.match(r'(Д|д)а', ans):
#            pass
#        elif re.match(r'(Н|н)ет', ans):
#            args['message'] = 'Ну тогда попробуй еще раз'
#            bot.Replyqueue.put(args)
#            return "error"
#        try:
#            execute(bot,
#                    RemoteData,
#                    False)
#        except Exception as E:
#
#            exc_type, exc_value, exc_traceback = sys.exc_info()
#            TB = traceback.format_tb(exc_traceback)
#
#            args['message'] = "Неудалось выполнить команду удалённо, ошибка:{}\n {}\n {} \n {}".format(exc_type,
#                                                                                                       exc_value,
#                                                                                                       ''.join(TB),
#                                                                                                       "Перешлите это сообщение владельцу бота")
#            bot.Replyqueue.put(args)







class Command_Zashkvar(C_template):
    name = ['зашквар', "жир"]
    access = ['user']
    desc = 'Замеряет зашкварность сообщения'
    perm = 'text.zashkvar'
    template = '{botname}, зашквар'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolMessage, LongPoolUpdates: Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", }
        if forward:
            args.update({"forward_messages": data.id})
        if len(data.fwd_messages)>0:
            try:
                message = data.fwd_messages[0]
                try:
                    temp = len(message.body)
                except:
                    temp = message.date
            except:
                args['message'] = "Непонятная ошибочка."
                bot.Replyqueue.put(args)
                return

            print(temp)
            random.seed(temp)
            zh = random.randint(0, 100)
            template = "Зашкварность - {}%"
            args['message'] = template.format(zh)
            bot.Replyqueue.put(args)


        else:
            args['message'] = "Нечего мерять. Прикрепи к команде сообшение, зашкварность которого хочешь померять"
            bot.Replyqueue.put(args)
