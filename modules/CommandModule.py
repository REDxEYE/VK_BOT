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

from utils.StringBuilder import StringBuilder

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

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        text = data.message[:-1] if '?' in data.message else data.message
        if int(data.chat_id) <= 2000000000:

            data.send_back("Тебя",fwd=True)
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
                data.send_back('Определённо меня',fwd=True)

            name = '*id{} ({} {})'.format(str(ud.id), ud.first_name_acc, ud.last_name_acc)
            replies = ["Определённо {}", "Точно {}", "Я уверен что его -  {}"]
            msg = random.choice(replies)
            data.send_back(msg.format(name),fwd=True)
            # self.Reply(self.UserApi, args)



@ModuleManager.command(names=["кто?"], perm='text.who', desc="Выбирает случайного человека", cost=2)
class Command_Who(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):

        text = data.text[:-1] if data.text.endswith('?') else data.text
        text = text.replace('мне', 'тебе')
        text = text.replace('мной', 'тобой')
        text = text.replace('моей', 'твоей')
        text = text.replace('меня', 'тебя')
        if not data.isChat:
            data.send_back("Ты")
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
                data.send_back("Ты {}".format(toins.replace("тебе", "себе")),[],True)
                return True
            if ud.id == self.api.MyUId:
                data.send_back('Определённо Я',[],True)

                return True
            name = '*id{} ({} {})'.format(str(ud.id), ud.first_name_nom, ud.last_name_nom)

            msg = random.choice(replies)
            data.send_back(msg.format(name, toins),[],True)


@ModuleManager.command(names=["вероятность"], perm='text.prob', desc="Процент правдивости инфы")
class Command_Prob(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        a = data.body.split(' ')
        if 'вероятность' in a[1]:
            a = a[2:]
        else:
            a = a[1:]
        msg = "Вероятность того, что {}, равна {}%".format(' '.join(a), random.randint(0, 100))
        data.send_back(msg,[],True)



@ModuleManager.command(names=["где"], desc='Говорит где что находится', perm='text.where')
class Command_Where(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        replies = ["Под столом", "На кровати", "За спиной", "На столе"]
        msg = random.choice(replies)
        data.send_back(msg,[],True)



@ModuleManager.command(names=["ты"], desc='Не обзывай бота', perm='text.you', template="{botname}, ты!")
class Command_You(C_template):
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
            msg = msg.format(' '.join(data.text.split(' ')))
        except:
            pass
        data.send_back(msg, [], True)
        return True


@ModuleManager.command(names=["команды", "помощь"], desc="Выводит это сообщение", perm='text.help',
                       template='"{botname}, помощь" или "{botname}, команды" - выводится список команд,\nа "{botname}, помощь НАЗВАНИЕ КОМАНДЫ" или "{botname}, команды НАЗВАНИЕ_КОМАНДЫ" - Выведет шаблон запроса')
class Command_Help(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        if len(data.args) >= 1 and data.args[0] != "":
            print(data.args)
            self.GetHelp(data, data.args[0])
            return
        UserPerms = self.api.USERS.GetPerms(data.user_id)
        all_commands = self.api.MODULES.GetAvailable(UserPerms)
        a = f"Вам доступно {len(all_commands)} \ {len(self.api.MODULES.MODULES)}:\n"

        for command in all_commands:
            a += 'Команда: "{}", {}.\n'.format('" или "'.join(command.names), command.desc)
        data.send_back(a, [], True)
        return True

    def GetHelp(self, data: LongPoolHistoryMessage, command):

        if self.api.MODULES.isValid(command):
            mod = self.api.MODULES.GetModule(command)
            msg = StringBuilder(sep='\n')
            msg += f'Команда: "{command}"'
            msg += f'Информация: {mod.desc}'
            msg += f'Альтернативы: {mod.names}'
            msg += f'Уровень доступа: {mod.perms}'
            if hasattr(mod.funk,'vars'):
                msg += 'Параметры:'
                for var in mod.funk.vars.get_vars:
                    msg += f"&#8192;>>{var.key}"
                    msg += f"&#8192;&#8192;&#8192;Описание: {var.desc}"
                    msg += f"&#8192;&#8192;&#8192;Обязателен: {var.required}"
                    msg += f"&#8192;&#8192;&#8192;Стандартное значене: {var.defval}"
                    if hasattr(var,'min_max'):
                        msg += f"&#8192;&#8192;&#8192;Минимум - максимум: {var.min_max[0]} - {var.mim_max[1]}"
            msg = msg.toString()

        else:
            msg = 'Неизвестная команда'
        data.send_back(msg, [], True)


@ModuleManager.command(names=["перешли"], desc="Пересылает фото", perm='text.resend', template="{botname}, перешли")
class Command_resend(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):


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
        data.send_back('Вотъ', Topost, True)
        return True


@ModuleManager.command(names=["изгнать", "kick", "votekick"], desc="Изгоняет пользователя", perm='chat.kick',
                       template="{botname}, изгнать UID1 UID2 UID3")
@ModuleManager.argument('id',0,'Id того кого нужно выгнать', False)
class Command_kick(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        ToKick = list(self.vars.id) if self.vars.has_var('id') else data.text.split(' ')
        if len(ToKick) < 1:
            return False

        for user in ToKick:
            if self.api.USERS.GetStatus(data.user_id) in ['admin', 'moder']:
                msg = "Нельзя кикать администрацию"
                data.send_back(msg, [], True)
                continue
            name = LongPoolUpdates.GetUserProfile(data.user_id)
            msg = "The kickHammer has spoken\n {} has been kicked in the ass".format(
                ' '.join([name.first_name, name.last_name]))
            print(data)
            self.api.UserApi.messages.removeChatUser(v=5.45, chat_id=data.chat_id - 2000000000, user_id=user)
            data.send_back(msg, [], True)
        return True


@ModuleManager.command(names=["5nights"], desc="Добавляет в беседу", perm='text.joinChat',
                       template="{botname}, 5nights")
class Command_JoinFiveNigths(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        are_friend = self.api.UserApi.friends.areFriends(user_ids=[data.user_id])[0]['friend_status']
        if int(are_friend) == 3:
            ans = self.api.UserApi.messages.addChatUser(chat_id=13, user_id=data.user_id)
            # ans = self.api.UserApi.messages.addChatUser(chat_id=22, user_id=data.user_id)

            if int(ans) != 1:
                msg = 'Ошибка добавления'
                data.send_back(msg, [], True)
                return False
            return True

        else:
            f = int(self.api.UserApi.friends.add(user_id=data.user_id, text='Что б добавить в беседу'))
            if f == 1 or f == 2:

                ans = self.api.UserApi.messages.addChatUser(chat_id=13, user_id=data.user_id)
                msg = 'Примите завяку и снова напишите !5nights'
                if int(ans) != 1:
                    msg = 'Ошибка добавления'
                data.send_back(msg, [], True)

            else:
                msg = 'Не могу добавить вас в друзья, а значит и не могу добавить в беседу'
                data.send_back(msg, [], True)
            return True



@ModuleManager.command(names=["инфо", "инфа", "info", 'stats', 'stat'], desc="Статистика", perm='text.info',
                       template='{botname}, инфо')
class Command_StatComm(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):


        string_ = StringBuilder(sep='\n')
        string_ += f'Кол-во обработанных сообщений: {self.api.Stat["messages"]}'
        string_ += f'Зарегестрировано польхователей: {len(self.api.USERS.DB)}'
        string_ += f'Размер кэша: {self.api.Stat["cache"]}'
        string_ += f'Кол-во живых потоков: {len([thread for thread in self.api.EX_threadList if thread.is_alive()])}'
        msg = string_.__str__()
        data.send_back(msg, [], True)
        return True


@ModuleManager.command(names=["дебаг"], desc="Врубает режим АдминОнли", perm='core.debug', template='{botname}, дебаг')
class Command_AdminOnly(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):

        self.api.AdminModeOnly = not self.api.AdminModeOnly
        msgOn = 'Включен режим дебага, принимаются сообщения только от админов'
        msgOff = 'Выключен режим дебага, принимаются все сообщения '
        msg = msgOn if self.api.AdminModeOnly else msgOff
        data.send_back(msg, [], True)
        return True



@ModuleManager.command(names=['about', 'ктоты'], desc='Выводит информацию о боте', perm='text.about',
                       template='{botname}, about')
class Command_About(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):


        msg = \
            'Создан *red_eye_rus (Red Dragon)\n' \
            'Множество идей взяты у *rukifox (Яна)\n' \
            # 'GitHub: www.github.com/REDxEYE/VK_BOT\n'
        data.send_back(msg, [], True)


# @ModuleManager.command(names=["namelock"], desc="Лочит имя беседы", perm='chat.LockName',template='{botname}, namelock')
class Command_LockName(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, forward=True):
        id = int(data.id)
        if id not in self.api.Settings['namelock']:
            msg = 'Смена названия беседы запрещена'
            self.api.Settings['namelock'].append(id)

        else:

            self.api.Settings['namelock'].remove(id)
            msg = 'Смена названия беседы разрешена'
        data.send_back(msg, [], True)
        self.api.SaveConfig()
        return True


@ModuleManager.command(names=["этослучилось", 'ithappens'], desc="Рандомная история с ithappens.me",
                       perm='text.Zadolbali', template='{botname}, этослучилось')
class Command_ithappens(C_template):

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
        feed = feedparser.parse('http://www.ithappens.me/rss')['entries']
        zz = random.choice(feed)
        template = """      {}

         {}
          {}"""
        msg = template.format(zz['title'], Command_ithappens.strip_tags(zz['summary']), zz['link'])

        data.send_back(msg, [], True)
        return True

        # if __name__ == "__main__":
        #    Command_Zadolbali().execute(None,{})


@ModuleManager.command(names=["блок"], desc="блокирует команду в чате", perm='chat.BlockCommand',
                       template='{botname}, блок\n' \
                                'команда:название команды\n')
@ModuleManager.argument('command','','Команда которую нужно забанить',True)
class Command_banCommand(C_template):


    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        comm = self.vars.command
        if comm in ['bannedCommands']:
            self.api.Settings['bannedCommands'][comm].append(str(data.id))
        else:
            self.api.Settings['bannedCommands'][comm] = [str(data.id)]


@ModuleManager.command(names=["выбери"], desc="Выбирает из представленных вариантов", perm='text.choice',
                       template='{botname}, вариант1 вариант2 вариант3 вариантN ')
class Command_Choice(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        var = random.choice(data.text.split(','))
        templates = ['Я выбираю: {}', "Вот это: {}", "Думаю это лучший вариант: {}"]
        msg = random.choice(templates).format(var)
        data.send_back(msg, [], True)


@ModuleManager.command(names=["скажи"],
                       desc='Произносит ваш текст на выбранном языке ("Имя бота", "нужный язык (2буквы)" " ВАШ ТЕКСТ")',
                       perm='text.tts', template='{botname}, нужный язык(2буквы) ВАШ ТЕКСТ)')
class Command_TTS(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        apiurl = f"https://api.vk.com/method/docs.getUploadServer?access_token={self.api.UserAccess_token}&type=audio_message&v=5.60"
        server = json.loads(urlopen(apiurl).read().decode('utf-8'))['response']['upload_url']

        lang = data.args[0]
        tosay = data.args[1:]
        if lang not in gtts.gTTS.LANGUAGES:
            lang = 'ru'
            tosay = data.args
        tts = gtts.gTTS(' '.join(tosay), lang=lang, debug=True)
        a = tempF.NamedTemporaryFile('w+b', suffix='.mp3', dir='tmp', delete=False)
        try:
            tts.write_to_fp(a)
        except:
            msg = 'Технические сложности. Обратитесь через пару секунд'
            data.send_back(msg, [], True)
            return
        a.close()
        req = requests.post(server, files={'file': open(a.name, 'rb')})
        os.remove(a.name)
        if req.status_code == requests.codes.ok:
            print('req', req.json())
            params = {'file': req.json()['file'], 'v': '5.60'}
            doc = self.api.UserApi.docs.save(**params)[0]

            Voice = 'doc{}_{}'.format(doc['owner_id'], doc['id'])

            data.send_back("", [Voice], True)


@ModuleManager.command(names=['зашквар', "жир"], desc='Замеряет зашкварность сообщения', perm='text.zashkvar',
                       template='{botname}, зашквар')
class Command_Zashkvar(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):

        if len(data.fwd_messages) > 0:
            try:
                message = data.fwd_messages[0]
                try:
                    temp = len(message.body)
                except:
                    temp = message.date
            except:
                msg = "Непонятная ошибочка."
                data.send_back(msg, [], True)
                return

            random.seed(temp)

            template = "Зашкварность - {}%"
            msg= template.format(random.randint(0, 100))
            data.send_back(msg, [], True)


        else:
            msg = "Нечего мерять. Прикрепи к команде сообшение, зашкварность которого хочешь померять"
            data.send_back(msg, [], True)
