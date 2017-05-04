import io
import queue
import random
import re
import threading
import urllib
from math import *
from time import sleep
from typing import overload
from urllib.request import urlopen
import requests
import vk.exceptions as VKEX
from PIL import Image
from vk import *
import trigger
from DataTypes.LongPoolHistoryUpdate import Updates, LongPoolHistoryMessage, FillUpdates
from DataTypes.attachments import attachment
from DataTypes.user import user
from DataTypes.group import group
from Module_manager_v2 import *
from Module_struct import Module
from User_Manager import *
from utils.StringBuilder import StringBuilder
from utils.cookies import get_cookies
from utils.cooldown import cooldown_manager
from libs.tempfile_ import *
import asyncio
try:
    import aiml_.Core
except ImportError:
    pass
import gc
import argparse

try:
    from chatterbot import ChatBot

    ChatBotAvalible = True
except ImportError:
    ChatBotAvalible = False
    ChatBot = None
from utils import ArgBuilder
from socket_server import Server
HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def getpath() -> str:
    """

    Returns:
        str: path to current file
    """
    return os.path.dirname(os.path.abspath(__file__))


def prettier_size(n, pow_=0, b=1024, u='B', pre=[''] + [p + 'i' for p in 'KMGTPEZY']) -> str:
    """

    Args:
        n:
        pow_:
        b:
        u:
        pre:

    Returns:
        str: converts size in bytes to size in kb,mb and etc
    """
    r, f = min(int(log(max(n * b ** pow_, 1), b)), len(pre) - 1), '{:,.%if} %s%s'
    return (f % (abs(r % (-r - 1)), pre[r], u)).format(n * b ** pow_ / b ** float(r))


class SessionCapchaFix(Session):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    def get_captcha_key(self, captcha_image_url) -> str:
        """
        Default behavior on CAPTCHA is to raise exception
        Reload this in child
        """
        print(captcha_image_url)
        cap = input('capcha text:')
        return cap


class Bot:
    def __init__(self, threads=4, DEBUG=False, token_only=False):
        self.token_only = token_only
        self.login = 0
        self.cookies_creation_time = 0
        self.pass_ = 0
        self.client_id = 0
        self.remixsed = 0
        self.Stat = {}
        self.prefix = '\\\\'
        self.Settings = {}
        self.GC = gc
        self.GC.enable()
        if ChatBotAvalible:
            self.chatbot = ChatBot('RED EYE',
                                   trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
                                   preprocessors=[
                                       'chatterbot.preprocessors.clean_whitespace',
                                       'chatterbot.preprocessors.unescape_html', ],
                                   logic_adapters=[
                                       {
                                           "import_path": "chatterbot.logic.BestMatch",
                                           "statement_comparison_function": "chatterbot.comparisons.jaccard_similarity",
                                           "response_selection_method": "chatterbot.response_selection.get_most_frequent_response"
                                       }])
            # self.chatbot.train("chatterbot.corpus.russian")
        self.ROOT = getpath()

        self.IMAGES = os.path.join(self.ROOT, 'IMAGES')

        self.Checkqueue = queue.Queue()
        self.Replyqueue = queue.Queue()
        self.Serverqueue = queue.Queue()
        self.LP_threads = []
        self.EX_threadList = []
        for i in range(threads):
            thread = threading.Thread(target=self.ExecCommands)
            thread.setName('Exec thread №{}'.format(i))
            thread.setDaemon(True)
            thread.start()
            self.EX_threadList.append(thread)
            print('Exec thread №{} started'.format(i))
        self.USERS = UserManager()
        self.MODULES = ModuleManager(self)
        self.DEBUG = DEBUG
        self.TRIGGERS = trigger.TriggerHandler()
        self.COOLDOWN = cooldown_manager(timeout=5, limit=3)
        self.AdminModeOnly = False

        self.defargs = {"v": "5.60"}

        self.LoadConfig()

        self.SaveConfig()

        self.UserAccess_token = self.Settings['UserAccess_token']
        self.remixsed_avalible = True
        self.check_remixsid()
        if 'GroupAccess_token' in self.Settings:
            self.GroupAccess_token = self.Settings['GroupAccess_token']
            self.GroupSession = SessionCapchaFix(access_token=self.GroupAccess_token)
            self.GroupApi = API(self.GroupSession)
        else:
            self.GroupApi = None

        self.UserSession = SessionCapchaFix(access_token=self.UserAccess_token)
        self.DefSession = SessionCapchaFix()

        self.UserApi = API(self.UserSession)
        self.DefApi = API(self.DefSession)

        self.log = io.open("Message_Log.Log", mode="ta", newline="\n", encoding="utf-8")

        self.ReplyThread = threading.Thread(target=self.Reply)
        self.ReplyThread.setDaemon(True)
        self.ReplyThread.setName('Reply Thread')
        self.ReplyThread.start()
        try:
            self.MyUId = self.UserApi.users.get(v='5.60')[0]['id']
        except:
            self.check_remixsid(True)
            self.UserSession = SessionCapchaFix(access_token=self.UserAccess_token)
            self.DefSession = SessionCapchaFix()

            self.UserApi = API(self.UserSession)
            self.DefApi = API(self.DefSession)
            self.MyUId = self.UserApi.users.get(v='5.60')[0]['id']

        self.MyName = self.GetUserNameById(self.MyUId, update=True)

        self.server = Server.Server(sender = self.send_to_chat,api = self,message_queue = self.Serverqueue, database = self.USERS)
        try:
            aiml_.Core.InitCore(self)
        except:
            pass
        print('LOADED')

    def send_to_chat(self,message,user_id,chat_id):
        print(message,user_id,chat_id)
        args = ArgBuilder.Args_message()
        args.setpeer_id(int(chat_id)+2000000000)
        args.setmessage(f"{self.GetUserNameById(user_id).Name}:{message}")
        self.Replyqueue.put(args)

    def get_chats(self):
        chats = self.UserApi.messages.getDialogs(count = 10,v= '5.60')['items']

        t = {}
        for chat in chats:
            try:
                t[chat['message']['chat_id']] = chat['message']['title']
            except KeyError:
                continue
        #chats = {a['message']['chat_id']:a['message']['title'] for a in chats}
        return t










    def check_remixsid(self, force=False):
        try:
            print(time.time() - self.cookies_creation_time)
            if time.time() - self.cookies_creation_time > 86400 and not force:
                self.remixsed, self.UserAccess_token = get_cookies(self.login, self.pass_, self.client_id)
                self.cookies_creation_time = time.time()
            elif force:
                self.remixsed, self.UserAccess_token = get_cookies(self.login, self.pass_, self.client_id)
                self.cookies_creation_time = time.time()
            self.Settings['UserAccess_token'] = self.UserAccess_token
            self.SaveConfig()
        except:
            self.remixsed_avalible = False

    def GetImg(self, name) -> str:
        """
 
        Args:
            name: Image name

        Returns:
            str:Path to img
        """
        if name in os.listdir(self.IMAGES):
            return os.path.join(self.IMAGES, name)

        else:
            raise FileNotFoundError('There is no file named {} in images folder'.format(name))

    def GetRandomImg(self, name) -> str:
        """

        Args:
            name: Image name for pattern NAME_([0-9]+)

        Returns:
            str:Path to img
        """
        patt = re.compile('{}_([0-9]+)'.format(name), re.IGNORECASE)
        results = list([file_name for file_name in os.listdir(self.IMAGES) if patt.findall(file_name)])



        if len(results) != 0:
            return os.path.join(self.IMAGES, random.choice(results))


        else:
            raise FileNotFoundError('There is no file named {} in images folder'.format(name))

    def GetUserFromMessage(self, message_id) -> str:
        """

        Args:
            message_id: Message id

        Returns:
            str:user id
        """

        uid = self.UserApi.messages.getById(message_ids=message_id, v="5.60")['items'][0]['user_id']
        return uid

    @staticmethod
    def html_decode(s):
        htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
        )
        for code in htmlCodes:
            s = s.replace(code[1], code[0])
        return s

    def GetUserNameById(self, Id, case='nom', update=False) -> user:

        """

        Args:
            update (bool): Use api instead of cached info
            Id (int): User ID
            case (str): case

        Returns:
            user:User data
        """
        print(Id, type_='GetUserNameById/DEBUG')
        if self.USERS.isCached(Id) and case == 'nom' and not update:
            #print('Using cached data for user {}'.format(Id))
            User = self.USERS.getCache(str(Id))

        else:
            try:
                User = self.UserApi.users.get(user_ids=Id, v="5.60",
                                              fields=['photo_id', 'verified', 'sex', 'bdate', 'city', 'country',
                                                      'home_town', 'has_photo', 'photo_50', 'photo_100',
                                                      'photo_200_orig', 'photo_200', 'photo_400_orig', 'photo_max',
                                                      'photo_max_orig', 'online', 'domain',
                                                      'has_mobile', 'contacts', 'site', 'education', 'universities',
                                                      'schools', 'status', 'last_seen',
                                                      'followers_count', 'common_count', 'occupation', 'nickname',
                                                      'relatives', 'relation', 'personal',
                                                      'connections', 'exports', 'wall_comments', 'activities',
                                                      'interests', 'music', 'movies', 'tv',
                                                      'books', 'games', 'about', 'quotes', 'can_post',
                                                      'can_see_all_posts', 'can_see_audio', 'can_write_private_message',
                                                      'can_send_friend_request', 'is_favorite', 'is_hidden_from_feed',
                                                      'timezone', 'screen_name', 'maiden_name',
                                                      'crop_photo', 'is_friend', 'friend_status', 'career', 'military',
                                                      'blacklisted', 'blacklisted_by_me', 'first_name_nom',
                                                      'first_name_gen',
                                                      'first_name_dat', 'first_name_acc', 'first_name_ins',
                                                      'first_name_abl', 'last_name_nom', 'last_name_gen',
                                                      'last_name_dat',
                                                      'last_name_acc', 'last_name_ins', 'last_name_abl'])[0]
                self.USERS.cacheUser(Id, User)
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                TB = traceback.format_tb(exc_traceback)
                print(TB, exc_type, exc_value)
                User = None

        return user.Fill(User)

    def Reply(self):
        while True:
            args = self.Replyqueue.get()
            if isinstance(args, ArgBuilder.Args_message):
                args = args.AsDict_()
            sleep(1)
            try:
                self.UserApi.messages.send(**args)
                self.Replyqueue.task_done()
            except VKEX.VkAPIError as Ex:
                sys.stderr.write('VkApi error - ' + str(Ex))
                self.Replyqueue.put(args)

    def generateConfig(self, path):
        token = input('User access token')
        self.USERS.WriteUser(input('Admin ID'), self.USERS.Stats.admin, self.USERS.Actions.Add, 'core.*', 'chat.*')
        data = {}
        with open(path + '/settings.json', 'w') as config:
            data['settings'] = {'UserAccess_token': token, "bannedCommands": {}}

            json.dump(data, config)

    def LoadConfig(self):
        path = getpath()
        if not os.path.exists(path + '/settings.json'):
            self.generateConfig(path)
        with open(path + '/settings.json', 'r') as config:
            settings = json.load(config)

            try:
                self.Stat = settings["stat"]
            except KeyError:
                self.Stat = {'messages': 0, 'commands': 0}
            try:
                self.prefix = settings['prefix']
            except KeyError:
                self.prefix = '\\\\'
            self.Settings = settings["settings"]

            if not self.token_only:
                try:
                    self.cookies_creation_time = settings['cookies']
                except KeyError:
                    print('No cookies')
                    self.cookies_creation_time = 0.0
                try:
                    self.login = settings['login']
                except KeyError:
                    print('No login')
                    self.login = input('Page login:')
                try:
                    self.pass_ = settings['pass']
                except KeyError:
                    print('No password')
                    self.pass_ = input('Page password:')
                try:
                    self.client_id = settings['client_id']
                except KeyError:
                    print('No client_id')
                    self.client_id = input('client_id:')
                try:
                    self.remixsed = settings['remixsed']
                except KeyError:
                    print('No remixsed')
                    self.remixsed = 0

    def SaveConfig(self):
        path = getpath()
        data = {}

        with open(path + '/settings.json', 'w') as config:
            data['stat'] = self.Stat
            data['prefix'] = self.prefix
            data['settings'] = self.Settings
            if not self.token_only:
                data['cookies'] = self.cookies_creation_time
                data['remixsed'] = self.remixsed
                data['login'] = self.login
                data['pass'] = self.pass_
                data['client_id'] = self.client_id
            json.dump(data, config, indent=4, sort_keys=True)

    def GetUploadServer(self):
        return self.UserApi.photos.getMessagesUploadServer()

    def UploadPhoto(self, urls: list) -> list:
        """

        Args:
            urls (list): list of strings ( urls )

        Returns:
            list: list of strings ( photo id )

        """
        atts = []

        if isinstance(urls, str):
            urls = [urls]
        i = 0
        for url in urls:
            i += 1
            print('downloading photo№{}'.format(i))
            server = self.GetUploadServer()['upload_url']
            req = urllib.request.Request(url, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            print('uploading photo №{}'.format(i))
            req = requests.post(server, files={'photo': open(Tmp.file_(), 'rb')})
            print('Done')
            Tmp.rem()

            if req.status_code == requests.codes.ok:
                try:
                    params = {'server': req.json()['server'], 'photo': req.json()['photo'], 'hash': req.json()['hash']}
                    photos = self.UserApi.photos.saveMessagesPhoto(**params)
                    for photo_ in photos:
                        atts.append(photo_['id'])
                except Exception:
                    continue
        return atts

    def UploadFromDisk(self, file) -> str:
        """

        Args:
            file (str):path to file

        Returns:
            str:photo id
        """
        try:
            self.Stat['cache'] = str(prettier_size((os.path.getsize(os.path.join(getpath(), 'tmp', 'cache.zip')))))
        except FileNotFoundError:
            self.Stat['cache'] = 'NO CACHE'
        server = self.GetUploadServer()['upload_url']

        print('uploading photo №')
        req = requests.post(server, files={'photo': open(file, 'rb')})

        print('Done')
        # req = requests.post(server,files = {'photo':img})
        if req.status_code == requests.codes.ok:
            # print('req',req.json())
            try:
                params = {'server': req.json()['server'], 'photo': req.json()['photo'], 'hash': req.json()['hash']}
                photo_ = self.UserApi.photos.saveMessagesPhoto(**params)[0]
                return photo_['id']
            except Exception as ex:
                print(ex.__traceback__)
                print(ex.__cause__)

                exc_type, exc_value, exc_traceback = sys.exc_info()
                TB = traceback.format_tb(exc_traceback)
                print(exc_type, exc_value, ''.join(TB))
                return 'Error'

    def UploadDocFromDisk(self, file):
        """

        Args:
            file (str):path to file

        Returns:
            str: doc id
            any: doc
        """
        server = self.UserApi.docs.getUploadServer()['upload_url']
        name = file.split('/')[-1]
        print('uploading file')
        req = requests.post(server, files={'file': open(file, 'rb')})
        print('Done')
        # req = requests.post(server,files = {'photo':img})
        if req.status_code == requests.codes.ok:
            # print('req',req.json())
            params = {'file': req.json()['file'], 'title': name, 'v': 5.53}
            doc_ = self.UserApi.docs.save(**params)[0]

            return f'doc{doc_["owner_id"]}_{doc_["id"]}', doc_

    def UploadDocsDisk(self, urls: list) -> list:
        """

        Args:
            urls (list): list of strings ( urls )

        Returns:
            list: list of strings ( doc )

        """
        atts = []

        if isinstance(urls, str):
            urls = [urls]
        i = 0
        for url in urls:
            i += 1
            print(f'downloading Doc№{i}')
            server = self.UserApi.docs.getUploadServer()['upload_url']
            req = urllib.request.Request(url, headers=HDR)
            doc = urlopen(req).read()
            name = url.split('/')[-1]
            Tmp = TempFile(doc, name.split('.')[-1])
            print('uploading file')
            req = requests.post(server, files={'file': open(Tmp.path_, 'rb')})
            Tmp.rem()
            print('Done')
            # req = requests.post(server,files = {'photo':img})
            if req.status_code == requests.codes.ok:
                # print('req',req.json())
                params = {'file': req.json()['file'], 'title': name, 'v': 5.53}
                doc_ = self.UserApi.docs.save(**params)[0]
                atts.append(f'doc{doc_["owner_id"]}_{doc_["id"]}')
        return atts

    from DataTypes.LongPoolHistoryUpdate import Updates


    def ExecCommands(self):

        def process_fwd_msg(message_: LongPoolHistoryMessage) -> LongPoolHistoryMessage:
            if message_.hasFwd:
                fwd = message_.fwd_messages[0]

                if fwd.hasAttachment:
                    message_.attachments.extend(fwd.attachments)
            return message_
        while True:
            PvUpdates = self.Checkqueue.get()
            for message in PvUpdates.messages: #type: LongPoolHistoryMessage
                try:
                    for peername, client in self.server.clients.items():
                        if client.connected_chat == int(message.chat_id)-2000000000:
                            a = f'{self.GetUserNameById(message.user_id).Name}: {message.body}'
                            print(a)
                            self.server.send_to(peername, a)
                except Exception as e:
                    print('queue exception')
                if message.hasAction:
                    self.SourceAct(message, PvUpdates)
                sleep(0.3)
                self.TRIGGERS.processTriggers(message)
                self.Stat['messages'] += 1
                self.SaveConfig()
                if self.AdminModeOnly:
                    if 0 <= self.USERS.GetStatusId(message.user_id):
                        continue
                defargs = ArgBuilder.Args_message().setpeer_id(message.chat_id).setforward_messages(message.id)

                self.print_message(message, PvUpdates)
                comm = message.body.split("\n")
                message.custom = {}
                for C in comm[1:]:
                    C = C.split(":")
                    message.custom[C[0].strip().lower()] = ':'.join(C[1:])


                pattern = "^{}, ?|^{}, ?|^{}, ?|^{}, ?".format(self.MyName.first_name.lower(), self.MyName.first_name,
                                                               'ред', "Ред")

                if (re.search(pattern, message.body) or message.body.startswith(self.prefix)) and int(
                        message.user_id) != int(self.MyUId):
                    message = process_fwd_msg(message)
                    if message.body.startswith(self.prefix):
                        Command = message.body[len(self.prefix):].split('\n')[0].split(' ')[0].lower()
                        message.args = message.body[len(self.prefix):].strip().split('\n')[0].split(' ')[1:]
                        message.message = message.body[len(self.prefix)+len(Command):].strip()
                        message.text = message.body[len(self.prefix)+len(Command):].strip()
                    else:
                        Command = re.split(pattern, comm[0])[-1]
                        Command_ = Command.split(' ')[0].lower()
                        message.message = Command[len(Command_):].strip()
                        message.text = Command[len(Command_):].strip()
                        message.args = Command.split(' ')[1:]
                        Command = Command_
                    if Command in self.Settings['bannedCommands']:
                        if message.chat_id in self.Settings['bannedCommands'][Command]:
                            self.Checkqueue.task_done()
                            continue
                    if self.MODULES.isValid(Command):
                        funk = self.MODULES.GetModule(Command, message.args) #type: Module
                        user = message.user_id
                        self.COOLDOWN.adduser(user).chechUsers()
                        if self.USERS.HasPerm(user, funk.perms) and self.MODULES.CanAfford(self.USERS.GetCurrency(user),
                                                                                           Command) and (
                                    self.COOLDOWN.canUse(user) or self.USERS.HasPerm(user, 'core.nolimit')):
                            self.COOLDOWN.useUser(user)


                            if hasattr(funk.funk,'vars'):
                                defargs.message = ''
                                msg = StringBuilder(sep = '\n')
                                for line in message.message.splitlines():
                                    funk.funk.vars.parse(line)
                                for var_ in funk.funk.vars.get_unfilled:
                                    print(var_)
                                    msg.append(f'Отсутствует обязательный параметр {var_.key}')
                                if funk.funk.vars.has_missing:
                                    self.Replyqueue.put(defargs.setmessage(msg.toSting()))
                                    self.Checkqueue.task_done()
                                    continue

                            if hasattr(funk.funk,'side'):
                                side = funk.funk.side
                                print(side)
                                if message.isChat and side == 2:
                                    defargs.message = 'Данную команду нельзя вызывать в чате'
                                    self.Replyqueue.put(defargs.AsDict_())
                                    self.Checkqueue.task_done()
                                    continue
                                elif not message.isChat and side == 1:
                                    defargs.message = 'Данную команду нельзя вызывать в личных сообщениях'
                                    self.Replyqueue.put(defargs.AsDict_())
                                    self.Checkqueue.task_done()
                                    continue


                            try:
                                print("Executing command {},\n arguments:{}".format(Command, message.args))
                                print(message)

                                stat = funk.funk(message, PvUpdates)
                                self.USERS.pay(user, funk.cost)
                                if stat == False:
                                    print(self.MyName)
                                    defargs['message'] = 'Неправильно оформлен запрос. Пример запроса : {}'.format(
                                        funk.template.format(botname=self.MyName.first_name))
                                    self.Checkqueue.task_done()
                                    self.Replyqueue.put(defargs)
                                    continue
                                if stat == 'Error':
                                    pass
                                self.Checkqueue.task_done()
                                self.Stat['commands'] += 1
                                self.SaveConfig()
                            except Exception as Ex:
                                print(Ex.__traceback__)
                                print(Ex.__cause__)
                                sleep(1)
                                if 'many requests per second' in str(Ex):
                                    print('Too many requests per second')
                                    # self.Checkqueue.put(data,timeout=5)
                                    continue

                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                TB = traceback.format_tb(exc_traceback)

                                defargs['message'] = "Не удалось выполнить, ошибка:{}\n {}\n {} \n {}".format(exc_type,
                                                                                                              exc_value,
                                                                                                              ''.join(
                                                                                                                  TB),
                                                                                                              "Перешлите это сообщение владельцу бота")
                                print(defargs['message'])
                                # self.Reply(self.UserApi, args)
                                try:
                                    self.Checkqueue.task_done()
                                except ValueError:
                                    pass
                                #self.Replyqueue.put(defargs)
                        elif not self.MODULES.CanAfford(self.USERS.GetCurrency(user), Command):
                            defargs["message"] = "Нехватает валюты. Попробуйте обратиться к администрации"
                            try:
                                self.Checkqueue.task_done()
                            except ValueError:
                                pass
                            self.Replyqueue.put(defargs)
                        elif not self.COOLDOWN.canUse(user) and not self.COOLDOWN.iswarned(user):
                            self.COOLDOWN.warned(user)
                            defargs[
                                "message"] = "Вы превысили лимит команд. Последующий спам команд будет увеличивать время отката на 10 секунд"
                            try:
                                self.Checkqueue.task_done()
                            except ValueError:
                                pass
                            self.Replyqueue.put(defargs)

                        elif not self.COOLDOWN.canUse(user) and self.COOLDOWN.iswarned(user):
                            continue

                        else:
                            print('"Недостаточно прав"')
                            defargs["message"] = "Недостаточно прав"
                            try:
                                self.Checkqueue.task_done()
                            except ValueError:
                                pass
                            self.Replyqueue.put(defargs)

                    elif ChatBotAvalible:
                        ans = self.chatbot.get_response(str(message.message))
                        defargs['message'] = ans
                        try:
                            self.Checkqueue.task_done()
                        except ValueError:
                            pass
                        self.Replyqueue.put(defargs)

    def print_message(self, data: LongPoolHistoryMessage, LongPoolData: Updates):
        data = copy.deepcopy(data)
        p = '[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]'
        emoji_pattern = re.compile(p, re.VERBOSE)
        data.body = emoji_pattern.sub('', data.body)

        def process_attachments(_data: LongPoolHistoryMessage, _LongPoolData: Updates):
            fwdMessages = []
            attachments_ = []

            def process_FWD(fwds: list, depth=1):

                for fwd in fwds:
                    # fwd = fwd_message()
                    if fwd.hasFwd:
                        process_FWD(fwd.fwd_messages, depth + 1)

                    templateFWD = '|{}{} : \n|{}| {}\n'
                    try:
                        try:
                            Tuser = _LongPoolData.GetUserProfile(fwd.user_id)
                            Tusr = Tuser.first_name + ' ' + Tuser.last_name
                            Tmsg = fwd.body.replace('<br>', '\n| ')
                            fwdMessages.append(
                                templateFWD.format('    ' * fwd.depth, Tusr, ' ' + '    ' * fwd.depth, Tmsg))
                        except Exception:
                            Tuser = user.Fill(self.USERS.getCache(fwd.user_id))
                            Tusr = Tuser.first_name + ' ' + Tuser.last_name
                            Tmsg = fwd.body.replace('<br>', '\n| ')
                            fwdMessages.append(
                                templateFWD.format('    ' * fwd.depth, Tusr, ' ' + '    ' * fwd.depth, Tmsg))
                    except Exception:
                        fwdMessages.append(templateFWD.format(' ', 'ERROR', '', 'ERROR'))
                        continue

            process_FWD(_data.fwd_messages)
            if _data.hasAttachment:
                for t in _data.attachments:
                    if t.type == attachment.types.photo:
                        template_attach = "{} : {}"
                        attachments_.append(template_attach.format(t.type, t.photo.GetHiRes))

            out = ''
            out += ''.join(fwdMessages) if len(fwdMessages) > 0 else ''
            out += '\n' if (len(fwdMessages) > 0) and (len(attachments_) > 0) else ''
            out += ('Attachments :\n ' + '\n'.join(attachments_[::-1])) if len(attachments_) > 0 else ""
            out += '\n' if len(attachments_) > 0 else ''
            return out

        try:
            user = LongPoolData.GetUserProfile(data.user_id)
            template = '{} : {} : \n| {}\n'

            template2 = '[ message_id : {} | peer_id : {} ]\n'

            subj = "PM" if "..." in data.title else data.title

            usr = user.Name

            msg = data.body.replace('<br>', '\n| ')

            attachments = process_attachments(data, LongPoolData)

            toPrint = template.format(subj, usr, msg) + attachments + template2.format(data.id,
                                                                                       data.chat_id) if self.DEBUG else '\n'
            print(toPrint, type_="message")
            self.log.write(toPrint)
            self.log.flush()
            os.fsync(self.log.fileno())
            # print(data)
        except Exception as ex:
            print(ex.__traceback__)
            print(ex.__cause__)

            exc_type, exc_value, exc_traceback = sys.exc_info()
            TB = traceback.format_tb(exc_traceback)
            print(exc_type, exc_value, ''.join(TB))
            pass

    def SourceAct(self, data: LongPoolHistoryMessage, LongPoolUpdate: Updates):
        """

        Args:
            data (LongPoolMessage): Message
            LongPoolUpdate (LongPoolUpdate): Updates
        """
        print('Что то с Актом пришло')
        Targs = {"peer_id": data.chat_id, "v": "5.60"}
        if type == 'chat_photo_update':
            ChatAdmin = data.admin_id
            if int(ChatAdmin) != int(self.MyUId):
                return
            if int(data.user_id) == int(self.MyUId):
                return
            img = Image.open(os.path.join(self.IMAGES, 'CHAT_IMG.jpg'))
            tmpf = {'chat_id': int(data.chat_id) - 2000000000, "crop_x": ((img.size[0] - 350) / 2),
                    'crop_y': (((img.size[1] - 350) / 2) - 30), 'crop_width': 350}
            Uurl = self.UserApi.photos.getChatUploadServer(**tmpf)
            req = requests.post(Uurl['upload_url'], files={'file1': open(self.GetImg('CHAT_IMG.jpg'), 'rb')})
            self.UserApi.messages.setChatPhoto(**{'file': req.json()['response']})

        # if type == 'chat_title_update':
        #    who = data.user_id
        #    if self.USERS.HasPerm(who, 'chat.title'):
        #        if int(data.user_id) == int(self.MyUId):
        #            return
        #        if data.action. != data['source_text']:
        #            if data.chat_id in self.Settings['namelock']:
        #                self.UserApi.messages.editChat(chat_id=data.chat_id - 2000000000,
        #                                               title=data['source_old_text'], v='5.60')
        #                Targs['message'] = 'Название беседы менять запрещено'
        #                self.Replyqueue.put(Targs)
        #            else:
        #                pass
        #        else:
        #            pass

        if type == 'chat_invite_user':
            ChatAdmin = data.admin_id
            if int(ChatAdmin) != self.MyUId:
                return
            who = data.user_id  # Кто пригласил
            target = data.action.action_mid  # Кого пригласил

            if int(target) == self.MyUId or int(who) == self.MyUId:
                print('Сам себя')
                return
            if (not self.USERS.HasPerm(who, 'chat.invite')) or self.USERS.GetStatusId(target) < 99:
                Targs['message'] = 'Вы не имеете права приглашать людей в данную беседу'
                self.Replyqueue.put(Targs)
                name = self.GetUserNameById(int(target))
                Targs['message'] = f"The kickHammer has spoken.\n {name.Name} has been kicked in the ass"
                self.UserApi.messages.removeChatUser(v=5.45, chat_id=data.chat_id - 2000000000, user_id=target)

            else:
                print('Приглашен администрацией')
        if type == 'chat_kick_user':
            if int(data.user_id) == int(self.MyUId):
                return

            if int(data.user_id) == int(data.action.action_mid):
                user = self.GetUserNameById(data.action.action_mid)
                print(user)
                try:
                    sex = user.sex
                    if sex == 2:
                        end = ''
                    if sex == 1:
                        end = 'а'
                    else:
                        end = 'о'
                except:
                    end = 'о'
                Targs['message'] = 'Оп, {} ливнул{} с подливой &#9786;'.format(user.Name, end)
            else:
                user = self.GetUserNameById(data.action.action_mid, case='acc')
                Targs['message'] = 'Оп, {} кикнули &#127770;'.format(user.Name)
            self.Replyqueue.put(Targs)

    def ContiniousMessageCheck(self, server=""):
        ts = 0
        key = 0
        while True:

            try:
                if (server == ''):
                    results = self.UserApi.messages.getLongPollServer()
                    server = results['server']
                    key = results['key']
                    ts = results['ts']

                url = 'https://{}?act=a_check&key={}&ts={}&wait=25&mode=2&version=1'
                try:
                    req = requests.request('GET', url.format(server, key, ts)).json()

                except Exception:
                    print('TIMEOUT ERROR, reconnecting in 5 seconds')
                    sleep(5)
                    server = ""
                    ts = ""
                    key = ""
                    continue
                if len(req['updates']) > 0:
                    hasMsg = False
                    for upd in req['updates']:
                        if 4 == upd[0]:
                            hasMsg = True
                            # print(upd)
                    if hasMsg:
                        self.parseLongPoolHistory(ts)
                        ts = req['ts']

            except:
                print('TIMEOUT ERROR, reconnecting in 5 seconds')
                sleep(5)
                server = ""
                ts = ""
                key = ""

    def parseLongPoolHistory(self, ts):
        resp = self.UserApi.messages.getLongPollHistory(ts=ts, v='5.63',
                                                        fields=['photo_id', 'verified', 'sex', 'bdate', 'city',
                                                                'country', 'home_town', 'has_photo', 'photo_50',
                                                                'photo_100',
                                                                'photo_200_orig', 'photo_200', 'photo_400_orig',
                                                                'photo_max', 'photo_max_orig', 'online', 'domain',
                                                                'has_mobile', 'contacts', 'site', 'education',
                                                                'universities', 'schools', 'status', 'last_seen',
                                                                'followers_count', 'common_count', 'occupation',
                                                                'nickname', 'relatives', 'relation', 'personal',
                                                                'connections', 'exports', 'wall_comments', 'activities',
                                                                'interests', 'music', 'movies', 'tv',
                                                                'books', 'games', 'about', 'quotes', 'can_post',
                                                                'can_see_all_posts', 'can_see_audio',
                                                                'can_write_private_message',
                                                                'can_send_friend_request', 'is_favorite',
                                                                'is_hidden_from_feed', 'timezone', 'screen_name',
                                                                'maiden_name',
                                                                'crop_photo', 'is_friend', 'friend_status', 'career',
                                                                'military', 'blacklisted', 'blacklisted_by_me',
                                                                'first_name_nom', 'first_name_gen',
                                                                'first_name_dat', 'first_name_acc', 'first_name_ins',
                                                                'first_name_abl', 'last_name_nom', 'last_name_gen',
                                                                'last_name_dat',
                                                                'last_name_acc', 'last_name_ins', 'last_name_abl'], )
        try:
            updates = FillUpdates(resp)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            TB = traceback.format_tb(exc_traceback)
            print(exc_type)
            print(exc_value)
            print('\n', '\n'.join(TB))
            return
        # print('\n', '\n'.join([str(m) for m in updates.messages]))
        self.Checkqueue.put(updates)


from utils.overload_fixed import Overload, signature


def MultipleStrCheck(string: str, list: list) -> bool:
    for item in list:
        if item in string:
            return True
    return False


def CustomTriggers(api: Bot):
    t1 = trigger.Trigger(
        cond=lambda data: MultipleStrCheck(data.body.lower(), ['python', 'питон']) and int(data.user_id) != int(
            api.MyUId), onetime=False, infinite=True,
        callback=lambda message, result: api.Replyqueue.put(ArgBuilder.Args_message()
            .setpeer_id(message.chat_id)
            .setmessage('Кто-то сказал питон?')
            .setattachment(
            [api.UploadFromDisk(api.GetRandomImg('python'))])))

    api.TRIGGERS.addTrigger(t1)


if __name__ == "__main__":
    s = time.time()
    parser = argparse.ArgumentParser(description='VkBot')
    parser.add_argument('-r', dest='resend', help='Switch - resend messages or not', action="store_true")
    parser.add_argument('-thr', dest='threads', help='Number of threads for commands', default=4)
    parser.add_argument('-t', dest='token_only', help='login via token', action="store_true", default=False)
    args = parser.parse_args()
    if args.resend:
        ArgBuilder.Args_message.DoNotResend()
    bot = Bot(DEBUG=True, threads=int(args.threads), token_only=args.token_only)
    CustomTriggers(bot)
    print(f'Loaded in {time.time()-s} seconds')
    bot.ContiniousMessageCheck()
