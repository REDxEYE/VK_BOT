import argparse
import os,os.path,random,queue,re,io,sys
import threading
import urllib
from time import sleep
from urllib.request import urlopen

import requests
from PIL import Image
from vk import *
from math import *
import vk.exceptions as VKEX

from DataTypes.LongPoolHistoryUpdate import LongPoolHistoryMessage, FillUpdates, Updates
from DataTypes.attachments import attachment

HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}





# utils and modules
import ConsoleLogger
import trigger
from DataTypes.user import user
from utils import ArgBuilder
from Module_manager_v2 import *
from Module_struct import Module
from User_Manager import *
from libs.tempfile_ import *
from utils.StringBuilder import StringBuilder
from utils.command_parser import Command_parser
from utils.cookies import get_cookies
from utils.cooldown import cooldown_manager

LOGGER = ConsoleLogger.ConsoleLogger('VK')


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
def getpath() -> str:
    """

    Returns:
        str: path to current file
    """
    return os.path.dirname(os.path.abspath(__file__))
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
    DEBUG = False
    token_only = False
    AdminModeOnly = False
    @classmethod
    def set_debug(cls,d):
        cls.DEBUG = d
    @classmethod
    def set_token_only(cls,b):
        cls.token_only = b
    @classmethod
    def set_admin_mode_only(cls,b):
        cls.AdminModeOnly = b
    def __init__(self,threads = 4,token_only = False):
        self.set_token_only(token_only)
        self.login = 0
        self.cookies_creation_time = 0
        self.pass_ = 0
        self.client_id = 0
        self.remixsid = 0
        self.Stat = {}
        self.prefix = '\\\\'
        self.Settings = {}
        self.ROOT = getpath()
        self.IMAGES = os.path.join(self.ROOT, 'IMAGES')

        self.Checkqueue = queue.Queue()

        self.LP_threads = []
        self.EX_threadList = []
        for i in range(threads):
            thread = threading.Thread(target=self.execute)
            thread.setName('Exec thread №{}'.format(i))
            thread.setDaemon(True)
            thread.start()
            self.EX_threadList.append(thread)
            LOGGER.info('Exec thread №{} started'.format(i))
        self.USERS = UserManager()
        self.MODULES = ModuleManager(self)
        self.TRIGGERS = trigger.TriggerHandler()
        self.COOLDOWN = cooldown_manager(timeout=5, limit=3)
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

        try:
            self.MyUId = self.UserApi.users.get(v='5.60')[0]['id']
        except:
            self.check_remixsid(True)
            self.UserSession = SessionCapchaFix(access_token=self.UserAccess_token)
            self.UserApi = API(self.UserSession)
            self.MyUId = self.UserApi.users.get(v='5.60')[0]['id']

        self.MyName = self.GetUserNameById(self.MyUId, update=True)

        pattern = "^{}, ?|^{}, ?|^{}, ?|^{}, ?".format(self.MyName.first_name.lower(), self.MyName.first_name,
                                                       'ред', "Ред")
        self.command_parser = Command_parser(self.prefix, pattern)

    def get_image(self, name) -> str:
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


    def check_remixsid(self, force=False):
        try:
            LOGGER.debug('Is token expired?',time.time() - self.cookies_creation_time)
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
            settings = json.load(config) #type: Dict[object]

            self.Stat = settings.get('stat',{'messages': 0, 'commands': 0})
            self.prefix = settings.get('prefix','\\\\')

            self.Settings = settings["settings"]

            if not self.token_only:
                try:
                    self.cookies_creation_time = settings['cookies']
                except KeyError:
                    LOGGER.warn('No cookies')
                    self.cookies_creation_time = 0.0
                try:
                    self.login = settings['login']
                except KeyError:
                    LOGGER.warn('No login')
                    self.login = input('Page login:')
                try:
                    self.pass_ = settings['pass']
                except KeyError:
                    LOGGER.warn('No password')
                    self.pass_ = input('Page password:')
                try:
                    self.client_id = settings['client_id']
                except KeyError:
                    LOGGER.warn('No client_id')
                    self.client_id = input('client_id:')
                try:
                    self.remixsed = settings['remixsed']
                except KeyError:
                    LOGGER.warn('No remixsed')
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

    def GetUserNameById(self, Id, case='nom', update=False) -> user:

        """

        Args:
            update (bool): Use api instead of cached info
            Id (int): User ID
            case (str): case

        Returns:
            user:User data
        """
        LOGGER.debug(Id)
        if self.USERS.isCached(Id) and case == 'nom' and not update:
            # print('Using cached data for user {}'.format(Id))
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

    def GetUploadServer(self):
        return self.UserApi.photos.getMessagesUploadServer(v=5.53)
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
            LOGGER.info('downloading photo№{}'.format(i))
            server = self.GetUploadServer()['upload_url']
            req = urllib.request.Request(url, headers=HDR)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            LOGGER.info('uploading photo №{}'.format(i))
            req = requests.post(server, files={'photo': open(Tmp.file_(), 'rb')})
            LOGGER.info('Done uploading photo #{}'.format(i))
            Tmp.rem()

            if req.status_code == requests.codes.ok:
                try:
                    params = {'server': req.json()['server'], 'photo': req.json()['photo'], 'hash': req.json()['hash'],"v":5.53}
                    photos = self.UserApi.photos.saveMessagesPhoto(**params)
                    for photo_ in photos:

                        atts.append("photo" + str(photo_['owner_id']) + "_" + str(photo_['id']))
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

        LOGGER.info('uploading photo')
        req = requests.post(server, files={'photo': open(file, 'rb')})
        

        LOGGER.info('Done uploading photo')
        # req = requests.post(server,files = {'photo':img})
        # print(req.status_code)
        if req.status_code == requests.codes.ok:
            # print('req',req.json())
            try:
                params = {'server': req.json()['server'], 'photo': req.json()['photo'], 'hash': req.json()['hash'],"v":5.53}
                photo_ = self.UserApi.photos.saveMessagesPhoto(**params)[0]
                # print("photo"+str(photo_['owner_id'])+"_"+str(photo_['id']))
                return "photo"+str(photo_['owner_id'])+"_"+str(photo_['id'])
            except Exception as ex:
                LOGGER.error(ex.__traceback__)
                LOGGER.error(ex.__cause__)

                exc_type, exc_value, exc_traceback = sys.exc_info()
                TB = traceback.format_tb(exc_traceback)
                LOGGER.error(exc_type, exc_value, ''.join(TB))
                return 'Error'
        else:
            raise Exception("Not OK code")
		

    def UploadDocFromDisk(self, file):
        """

        Args:
            file (str):path to file

        Returns:
            str: doc id
            any: doc
        """
        server = self.UserApi.docs.getUploadServer(v=5.53)['upload_url']
        name = file.split('/')[-1]
        LOGGER.info('uploading file')
        req = requests.post(server, files={'file': open(file, 'rb')})
        LOGGER.info('Done uploading file')
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
            LOGGER.info(f'downloading Doc№{i}')
            server = self.UserApi.docs.getUploadServer(v=5.53)['upload_url']
            req = urllib.request.Request(url, headers=HDR)
            doc = urlopen(req).read()
            name = url.split('/')[-1]
            Tmp = TempFile(doc, name.split('.')[-1])
            LOGGER.info('uploading file')
            req = requests.post(server, files={'file': open(Tmp.path_, 'rb')})
            Tmp.rem()
            LOGGER.info('Done uploading file')
            # req = requests.post(server,files = {'photo':img})
            if req.status_code == requests.codes.ok:
                # print('req',req.json())
                params = {'file': req.json()['file'], 'title': name, 'v': 5.53}
                doc_ = self.UserApi.docs.save(**params)[0]
                atts.append(f'doc{doc_["owner_id"]}_{doc_["id"]}')
        return atts

    def SourceAct(self, message: LongPoolHistoryMessage, LongPoolUpdate: Updates):
        """

        Args:
            message (LongPoolMessage): Message
            LongPoolUpdate (LongPoolUpdate): Updates
        """
        LOGGER.debug('Что то с Актом пришло')
        if type == 'chat_photo_update':
            ChatAdmin = message.admin_id
            if int(ChatAdmin) != int(self.MyUId):
                return
            if int(message.user_id) == int(self.MyUId):
                return
            img = Image.open(os.path.join(self.IMAGES, 'CHAT_IMG.jpg'))
            tmpf = {'chat_id': int(message.chat_id) - 2000000000, "crop_x": ((img.size[0] - 350) / 2),
                    'crop_y': (((img.size[1] - 350) / 2) - 30), 'crop_width': 350}
            Uurl = self.UserApi.photos.getChatUploadServer(**tmpf)
            req = requests.post(Uurl['upload_url'], files={'file1': open(self.get_image('CHAT_IMG.jpg'), 'rb')})
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
            ChatAdmin = message.admin_id
            if int(ChatAdmin) != self.MyUId:
                return
            who = message.user_id  # Кто пригласил
            target = message.action.action_mid  # Кого пригласил

            if int(target) == self.MyUId or int(who) == self.MyUId:
                LOGGER.debug('Сам себя')
                return
            if (not self.USERS.HasPerm(who, 'chat.invite')) or self.USERS.GetStatusId(target) < 99:
                message.send_back(message = 'Вы не имеете права приглашать людей в данную беседу')
                name = self.GetUserNameById(int(target))
                message.send_back(message=f"The kickHammer has spoken.\n {name.Name} has been kicked in the ass")
                self.UserApi.messages.removeChatUser(v=5.45, chat_id=message.chat_id - 2000000000, user_id=target)

            else:
                LOGGER.debug('Приглашен администрацией')
        if type == 'chat_kick_user':
            if int(message.user_id) == int(self.MyUId):
                return

            if int(message.user_id) == int(message.action.action_mid):
                user = self.GetUserNameById(message.action.action_mid)
                # print(user)
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
                message.send_back(message= 'Оп, {} ливнул{} с подливой &#9786;'.format(user.Name, end))
            else:
                user = self.GetUserNameById(message.action.action_mid, case='acc')
                message.send_back(message= 'Оп, {} кикнули &#127770;'.format(user.Name))
    @staticmethod
    def process_fwd_msg(message_: LongPoolHistoryMessage) -> LongPoolHistoryMessage:
        if message_.hasFwd:
            fwd = message_.fwd_messages[0]

            if fwd.hasAttachment:
                message_.attachments.extend(fwd.attachments)
        return message_
    def execute(self):
        while True:
            PvUpdates = self.Checkqueue.get()
            for message in PvUpdates.messages:  # type: LongPoolHistoryMessage
                self.print_message(message, PvUpdates)
                message.set_api(self)
                if message.hasAction:
                    self.SourceAct(message, PvUpdates)
                self.TRIGGERS.processTriggers(message)
                self.Stat['messages'] += 1
                self.SaveConfig()
                if self.AdminModeOnly:
                    if 0 <= self.USERS.GetStatusId(message.user_id):
                        continue
                if self.command_parser.check_for_command(message.body) and int(message.user_id) != int(self.MyUId):
                    message = self.process_fwd_msg(message)
                    Command, message.name_args,message.args, message.text = self.command_parser.parse(message.body)

                    message.message = message.text
                    if Command in self.Settings['bannedCommands']:
                        if message.chat_id in self.Settings['bannedCommands'][Command]:
                            self.Checkqueue.task_done()
                            continue
                    if self.MODULES.isValid(Command):
                        LOGGER.debug('Executed command {}'.format(Command))
                        funk = self.MODULES.GetModule(Command, message.args)  # type: Module
                        user = message.user_id
                        self.COOLDOWN.adduser(user).chechUsers()
                        if self.USERS.HasPerm(user, funk.perms) and (self.COOLDOWN.canUse(user) or self.USERS.HasPerm(user, 'core.nolimit')):
                            self.COOLDOWN.useUser(user)
                            if hasattr(funk.funk, 'vars'):
                                msg = StringBuilder(sep='\n')
                                for line in message.message.splitlines():
                                    funk.funk.vars.parse(line)
                                for var_ in funk.funk.vars.get_unfilled:
                                    # print(var_)
                                    msg.append(f'Отсутствует обязательный параметр {var_.key}')
                                if funk.funk.vars.has_missing:
                                    message.send_back(msg.toString(),[],True)

                                    continue

                            if hasattr(funk.funk, 'side'):
                                side = funk.funk.side
                                # print(side)
                                if message.isChat and side == Workside.pm:
                                    message.send_back('Данную команду нельзя вызывать в чате',[],True)


                                    continue
                                elif not message.isChat and side == Workside.chat:
                                    message.send_back('Данную команду нельзя вызывать в личных сообщениях',[],True)


                                    continue

                            try:
                                LOGGER.debug("Executing command {},\n arguments:{}".format(Command, message.args))
                                # print(message)

                                stat = funk.funk(message, PvUpdates)
                                # self.USERS.pay(user, funk.cost)
                                if stat == 'Error':
                                    pass
                                self.Stat['commands'] += 1
                                self.SaveConfig()
                            except VKEX.VkAPIError as E:  # type: VKEX.VkAPIError
                                E = E  # type: VKEX.VkAPIError
                                LOGGER.warn(E.code)
                                LOGGER.warn(E.message)
                                sleep(1)
                                if E.code == 6:
                                    LOGGER.warn('Too many requests per second')
                                    # self.Checkqueue.put(data,timeout=5)
                                    continue

                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                TB = traceback.format_tb(exc_traceback)

                                # message.send_back("Не удалось выполнить, ошибка:{}\n {}\n {} \n {}".format(exc_type,
                                #                                                                            exc_value,
                                #                                                                            ''.join(
                                #                                                                                TB),
                                #                                                                            "Перешлите это сообщение владельцу бота"),[],True)
                                # print(defargs['message'])
                        elif not self.COOLDOWN.canUse(user) and not self.COOLDOWN.iswarned(user):
                            self.COOLDOWN.warned(user)
                            message.send_back("Вы превысили лимит команд. Последующий спам команд будет увеличивать время отката на 10 секунд",[],True)

                        elif not self.COOLDOWN.canUse(user) and self.COOLDOWN.iswarned(user):
                            continue

                        else:
                            # print('"Недостаточно прав"')
                            message.send_back("Недостаточно прав",[],True)
    def ContiniousMessageCheck(self, server=""):
        ts = 0
        key = 0
        while True:

            try:
                if server == '':
                    results = self.UserApi.messages.getLongPollServer(v=5.63)
                    server = results['server']
                    key = results['key']
                    ts = results['ts']

                url = 'https://{}?act=a_check&key={}&ts={}&wait=25&mode=2&version=1'
                try:
                    req = requests.request('GET', url.format(server, key, ts)).json()

                except Exception:
                    LOGGER.error('TIMEOUT ERROR, reconnecting in 5 seconds')
                    sleep(5)
                    server = ""
                    ts = ""
                    key = ""
                    continue
                if 'updates' not in req:
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

            except Exception as Exc:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                TB = traceback.format_tb(exc_traceback)
                print(exc_type,exc_value,'\n'.join(TB))
                print(Exc)
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

            toPrint = template.format(subj, usr, msg) + attachments + (template2.format(data.id, data.chat_id) if self.DEBUG else '\n')

            print(toPrint)
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


if __name__ == "__main__":
    s = time.time()
    parser = argparse.ArgumentParser(description='VkBot')
    parser.add_argument('-r', dest='resend', help='Switch - resend messages or not', action="store_true",default=True)
    parser.add_argument('-thr', dest='threads', help='Number of threads for commands', default=4)
    parser.add_argument('-t', dest='token_only', help='login via token', action="store_true", default=False)
    parser.add_argument('-d', dest='debug', help='DEBUG MODE', action="store_true", default=False)
    args = parser.parse_args()
    if args.resend:
        ArgBuilder.Args_message.DoResend()
    else:
        ArgBuilder.Args_message.DoNotResend()
    bot = Bot(threads=int(args.threads), token_only=args.token_only)
    bot.set_debug(args.debug)
    # CustomTriggers(bot)
    LOGGER.info(f'Loaded in {time.time()-s} seconds')
    bot.ContiniousMessageCheck()