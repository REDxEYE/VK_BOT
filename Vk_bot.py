import atexit
import json
import logging
import logging.config
import queue
import random
import re
import threading
from datetime import datetime, timedelta
from math import ceil
from time import sleep
from urllib.request import urlopen

import requests
from vk.exceptions import VkAuthError, VkAPIError
from vk.logs import LOGGING_CONFIG
from vk.utils import stringify_values, json_iter_parse, LoggingSession, str_type

import DA_Api as D_A
import Vk_bot_RssModule
import YT_Api as YT_
import e621_Api as e6
from Mimimi_Api import *
from tempfile_ import *

V = 3.0
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('vk')


def getpath():
    return os.path.dirname(os.path.abspath(__file__))


class SessionCapchaFix(object):
    API_URL = 'https://api.vk.com/method/'

    def __init__(self, access_token=None):

        logger.debug('API.__init__(access_token=%(access_token)r)', {'access_token': access_token})

        self.access_token = access_token
        self.access_token_is_needed = False

        self.requests_session = LoggingSession()
        self.requests_session.headers['Accept'] = 'application/json'
        self.requests_session.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    @property
    def access_token(self):
        logger.debug('Check that we need new access token')
        if self.access_token_is_needed:
            logger.debug('We need new access token. Try to get it.')
            self.access_token = self.get_access_token()
        else:
            logger.debug('Use old access token')
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value
        if isinstance(value, str_type) and len(value) >= 12:
            self.censored_access_token = '{}***{}'.format(value[:4], value[-4:])
        else:
            self.censored_access_token = value
        logger.debug('access_token = %r', self.censored_access_token)
        self.access_token_is_needed = not self._access_token

    def get_user_login(self):
        logger.debug('Do nothing to get user login')

    def get_access_token(self):
        """
        Dummy method
        """
        logger.debug('API.get_access_token()')
        return self._access_token

    def make_request(self, method_request, captcha_response=None):

        logger.debug('Prepare API Method request')

        response = self.send_api_request(method_request, captcha_response=captcha_response)
        # todo Replace with something less exceptional
        response.raise_for_status()

        # there are may be 2 dicts in one JSON
        # for example: "{'error': ...}{'response': ...}"
        for response_or_error in json_iter_parse(response.text):
            if 'response' in response_or_error:
                # todo Can we have error and response simultaneously
                # for error in errors:
                #     logger.warning(str(error))

                return response_or_error['response']

            elif 'error' in response_or_error:
                error_data = response_or_error['error']
                error = VkAPIError(error_data)

                if error.is_captcha_needed():
                    captcha_key = self.get_captcha_key(error.captcha_img)
                    if not captcha_key:
                        raise error

                    captcha_response = {
                        'sid': error.captcha_sid,
                        'key': captcha_key,
                    }
                    return self.make_request(method_request, captcha_response=captcha_response)

                elif error.is_access_token_incorrect():
                    logger.info('Authorization failed. Access token will be dropped')
                    self.access_token = None
                    return self.make_request(method_request)

                else:
                    raise error

    def send_api_request(self, request, captcha_response=None):
        url = self.API_URL + request._method_name
        method_args = request._api._method_default_args.copy()
        method_args.update(stringify_values(request._method_args))
        access_token = self.access_token
        if access_token:
            method_args['access_token'] = access_token
        if captcha_response:
            method_args['captcha_sid'] = captcha_response['sid']
            method_args['captcha_key'] = captcha_response['key']
        timeout = request._api._timeout
        response = self.requests_session.post(url, method_args, timeout=timeout)
        return response

    def get_captcha_key(self, captcha_image_url):
        """
        Default behavior on CAPTCHA is to raise exception
        Reload this in child
        """
        print(captcha_image_url)
        cap = input('capcha text:')
        return cap

    def auth_code_is_needed(self, content, session):
        """
        Default behavior on 2-AUTH CODE is to raise exception
        Reload this in child
        """
        raise VkAuthError('Authorization error (2-factor code is needed)')

    def auth_captcha_is_needed(self, content, session):
        """
        Default behavior on CAPTCHA is to raise exception
        Reload this in child
        """
        raise VkAuthError('Authorization error (captcha)')

    def phone_number_is_needed(self, content, session):
        """
        Default behavior on PHONE NUMBER is to raise exception
        Reload this in child
        """
        logger.error('Authorization error (phone number is needed)')
        raise VkAuthError('Authorization error (phone number is needed)')


class API(object):
    def __init__(self, session, timeout=10, **method_default_args):
        self._session = session
        self._timeout = timeout
        self._method_default_args = method_default_args

    def __getattr__(self, method_name):
        return Request(self, method_name)

    def __call__(self, method_name, **method_kwargs):
        return getattr(self, method_name)(**method_kwargs)


class Request(object):
    __slots__ = ('_api', '_method_name', '_method_args')

    def __init__(self, api, method_name):
        self._api = api
        self._method_name = method_name

    def __getattr__(self, method_name):
        return Request(self._api, self._method_name + '.' + method_name)

    def __call__(self, **method_args):
        self._method_args = method_args
        return self._api._session.make_request(self)
class VK_Bot:
    def __init__(self, threads=4):

        self.Checkqueue = queue.Queue()
        self.Replyqueue = queue.Queue()
        print('Loading')
        self.LoadConfig()
        for _ in range(threads):
            self.t = threading.Thread(target=self.CheckForCommands)
            self.t.setDaemon(True)
            self.t.start()
            print('Поток обработки сообщений создан')
        self.y = threading.Thread(target=self.Reply)
        self.y.setDaemon(True)
        self.y.start()
        print('Поток обработки ответов создан')

        self.Group = self.Settings['Group']
        self.GroupDomain = self.Settings['Domain']
        self.GroupAccess_token = self.Settings['GroupAccess_token']
        self.UserAccess_token = self.Settings['UserAccess_token']
        self.UserSession = SessionCapchaFix(access_token=self.UserAccess_token)
        self.GroupSession = SessionCapchaFix(access_token=self.GroupAccess_token)
        self.UserApi = API(self.UserSession)
        self.GroupApi = API(self.GroupSession)
        self.MyUId = self.UserApi.users.get()[0]['uid']
        self.MyName = self.GetUserNameById(self.MyUId)
        self.hello = re.compile(
            '(прив(|а|ет(|ик)(|ствую))|ку(|(-| )ку|)|х(а|е)й|зд((о|а)ров(а|)|ра(е|ь)|вствуй(|те)))|добр(ое|ый) (день|утро|вечер)')
        self.oldMsg = ""
        self.OldStat = self.UserApi.status.get()['text']
        self.UserApi.status.set(text="Bot online")

        print(self.OldStat)

    def GetChatName(self, id):
        url = 'https://api.vk.com/method/{}?{}&access_token={}'.format('messages.getChat', 'chat_id={}'.format(id),
                                                                       self.Settings['UserAccess_token'])
        resp = requests.get(url).json()

        return resp['response']

    def ClearPosts(self, Posts=None, treshholdTime=10, treshholdLikes=10):
        if Posts == None:
            Posts = self.CheckWall(self.GroupDomain)
        Currtime = datetime.now()
        for post in Posts:
            PostTime = datetime.fromtimestamp(post['date'])
            elapsedTime = Currtime - PostTime
            if (elapsedTime.seconds / 60 < treshholdTime) and (int(post['likes']['count']) < treshholdLikes):
                self.CreateComment(post=post['id'], text="Тестовое сообщение!(Проверка работы бота)", group=self.Group,
                                   owner=1)

    def CreateComment(self, post, text, group=None, owner=1):
        if group == None:
            group = self.Group

        self.UserApi.wall.createComment(owner_id=group, post_id=post, from_group=owner, message=text)

    def GetUserNameById(self, Id):
        # print('GetUserNameById: ', Id)
        sleep(0.01)
        try:
            User = self.UserApi.users.get(user_ids=Id, fields=['sex'])[0]
        except:
            return None
        return User

    def GetCommentsFromPost(self, GroupId, PostId, count):
        comments = []
        comms = []
        for _ in range(0, ceil(count / 100)):
            sleep(0.25)
            for Com in self.UserApi.wall.getComments(owner_id=GroupId, post_id=PostId, count=100)[1:]:
                comments.append(Com)
        for comment in comments:
            comms.append([self.GetUserNameById(comment['uid']), comment['text']])
        Out = ""
        for comm in comms:
            Out += comm[0] + " : " + comm[1] + "\n"
        return Out

    def CheckWall(self, GroupDomain):
        # bans = api.groups.getBanned(group_id="75615891")
        self.Wall = self.UserApi.wall.get(domain=GroupDomain, filter="others", count=10)
        self.posts = self.Wall[1:]
        Out = ""
        # print(self.posts[1])
        for I in self.posts:
            # comms = self.GetCommentsFromPost(I['to_id'],I['id'],I['reply_count'])
            # print(I)
            sleep(0.25)
            self.Data = datetime.fromtimestamp(I['date'])
            self.LikeCount = I['likes']['count']
            # print("Кол-во лайков: ",LikeCount)
            if I['text']:
                Text = I['text']
            else:
                Text = "Без текста"
            FIO = self.GetUserNameById(I["from_id"])
            ID = I["from_id"]
            Out += FIO + " : " + str(ID) + "\n"
            Out += Text + '\n'
            Out += "Кол-во лайков: " + str(self.LikeCount) + "\n"
            Out += "Дата: " + str(self.Data) + "\n"
            # Out += "Комментарии:\n" +Комментарии+"\n"
            Out += '\n\n'
        return Out

    def GetChats(self):
        self.messages = self.UserApi.messages.get()
        for M in self.messages[1:250]:
            # print(M)
            print("беседа: ", M['title'], self.GetUserNameById(M["uid"]), ":  ", M["body"])
            # print(it[8]["from_id"])

    def MakePost(self, command):
        args = {}
        if "группа" in command:
            args["owner_id"] = int(command["группа"])
        else:
            args["owner_id"] = self.Group
        if "текст" in command:
            text = command["текст"]
            args["message"] = text
        if "отгруппы" in command:
            args["from_group"] = command["отгруппы"]
        else:
            args["from_group"] = 1
        if "подпись" in command:
            args['singed'] = command["подпись"]
        else:
            args['singed'] = 1

        # print(args)
        # Post_id = self.UserApi.wall.post(owner_id = Group,message = text,from_group = from_group,signed = signed)
        Post_id = self.Post(args)
        if Post_id:
            return True
        else:
            return False

    def Post(self, args):
        return self.UserApi.wall.post(**args)

    def BanUser(self, args):
        SArgs = {}
        uid = int(args["id"])
        if "причина" in args:
            reason = int(args["причина"])
            SArgs['reason'] = reason
        if "группа" in args:
            SArgs['group_id'] = args["группа"]
        else:
            SArgs['group_id'] = self.Group.replace("-", "")
        SArgs['user_id'] = uid
        if args["комментарий"]:
            comment = args["комментарий"]
            SArgs['comment'] = comment
            SArgs['comment_visible'] = 1

        if "время" in args:
            end_date = datetime.timestamp(datetime.now() + timedelta(hours=int(args["время"])))
            SArgs["end_date"] = end_date
        ret = self.Ban(SArgs)

        if ret == 1:
            return True
        else:
            return False

    def Ban(self, args):
        return self.UserApi.groups.banUser(**args)

    def LoadConfig(self):
        path = getpath()
        with open(path + '/settings.json', 'r') as config:
            settings = json.load(config)
            self.UserGroups = settings["users"]
            print('User groups: ', self.UserGroups)
            self.Settings = settings["settings"]

    def SaveConfig(self):
        path = getpath()
        data = {}
        with open(path + '/settings.json', 'w') as config:
            data['users'] = self.UserGroups
            data['settings'] = self.Settings
            json.dump(data, config)

    def AddUser(self, args):
        print('Adduser: ', args)
        if "группа" in args:
            Group = args['группа'].lower()
        else:
            Group = "user"

        if 'id' in args:
            print(Group in self.UserGroups)
            if Group in self.UserGroups.keys():
                Ids = self.UserGroups[Group]
                Ids.append(int(args['id']))
                self.UserGroups[Group] = Ids
            else:
                self.UserGroups[Group] = [int(args['id'])]

            MArgs = {}
            MArgs['peer_id'] = args['args']['peer_id']

            userName = self.GetUserNameById(args['id'])
            MArgs['message'] = userName['first_name'] + ' ' + userName['last_name'] + ' был добавлен как ' + Group
            MArgs['v'] = 5.38
            print('Adduser reply: ', MArgs)
            # self.Reply(self.UserApi, MArgs)
            self.Replyqueue.put(MArgs)
            self.SaveConfig()

            return True
        else:
            return False

    def ExecCommand(self, command, args):
        print('executing command: ', command, ' with args:')
        print(args)
        return command(args)

    def GetRss(self, args):
        print('GetRss ', args)
        # comm = args['rss'].replace(" ", "").lower()
        url = args['url']
        rss = Vk_bot_RssModule.RssParser(url=url)
        news = rss.Parse()[:5]
        # rss = RssBot.Parse()

        for r in news:
            # print(r)
            Margs = {}
            Margs['v'] = 5.38
            Margs['peer_id'] = args['args']['peer_id']
            msg = str(r['date']) + '\n'
            msg += r['title'] + '\n'
            try:
                msg += r['link']
            except:
                pass
            atts = self.UploadPhoto(r['img'])
            Margs['attachment'] = atts
            Margs['message'] = msg
            # self.Reply(self.UserApi, Margs)
            self.Replyqueue.put(Margs)
            sleep(1)
        return True

    def Reply(self):
        print('Unfinished Reply tasks:', self.Replyqueue.unfinished_tasks)
        while True:
            args = self.Replyqueue.get()
            # print('Reply:', args)
            sleep(1)
            try:
                self.UserApi.messages.send(**args)
            except Exception as Ex:
                print("error couldn't send message:", Ex)
                args['message'] += '\nФлудконтроль:{}'.format(randint(0, 255))
                self.Replyqueue.put(args)
            self.Replyqueue.task_done()


    def GetUploadServer(self):
        return self.UserApi.photos.getMessagesUploadServer()

    def UploadPhoto(self, urls):
        atts = []
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        if type(urls) != type(['1', '2']):
            urls = [urls]
        i = 0
        for url in urls:
            i += 1
            print('downloading photo№{}'.format(i))
            server = self.GetUploadServer()['upload_url']
            req = urllib.request.Request(url, headers=hdr)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')

            args = {}
            args['server'] = server
            print('uploading photo №{}'.format(i))
            req = requests.post(server, files={'photo': open(Tmp.file_(), 'rb')})
            print('Done')
            Tmp.rem()

            # req = requests.post(server,files = {'photo':img})
            if req.status_code == requests.codes.ok:
                # print('req',req.json())
                photo = 'photo' + str(i)
                try:
                    params = {'server': req.json()['server'], 'photo': req.json()['photo'], 'hash': req.json()['hash']}
                    photos = self.UserApi.photos.saveMessagesPhoto(**params)
                    for photo in photos:
                        atts.append(photo['id'])
                except:
                    continue
        return atts

    def Music(self, args):
        name = args['имя']
        T_args = {}
        T_args['q'] = name
        tracks = self.UserApi.audio.search(**T_args)[1:]

        R_args = {}
        atts = []
        R_args['peer_id'] = args['args']['peer_id']
        # print(R_args)
        R_args['v'] = 5.38
        R_args['message'] = 'Песни по запросу {}'.format(name)
        print(tracks[0])
        for track in tracks:
            print(track)
            atts.append('audio{}_{}'.format(track['owner_id'], track['aid']))
        # print(atts)

        R_args['attachment'] = atts
        # print('ats',atts)
        # self.Reply(self.UserApi, R_args)
        args['forward_messages'] = args['data']['message_id']
        self.Replyqueue.put(R_args)

        return True
        # print(tracks)

    def e621(self, args):
        R_args = {}
        print(args)
        R_args['peer_id'] = args['args']['peer_id']
        tags = args['tags'].split(';')
        n = int(args['n'])
        try:
            page = int(args['page'])
        except:
            page = 1
        try:
            sort_ = args['sort'].replace(' ', '')
        except:
            sort_ = 'random'
        imgs = e6.get(tags=tags, n=n, page=page, sort_=sort_)
        atts = self.UploadPhoto(imgs)
        R_args['attachment'] = atts
        R_args['v'] = 5.38
        R_args['message'] = 'Вот порнушка по твоему запросу, шалунишка...'
        # self.Reply(self.UserApi, R_args)
        args['forward_messages'] = args['data']['message_id']
        self.Replyqueue.put(R_args)

        return True

    def D_A(self, args):
        R_args = {}
        R_args['peer_id'] = args['args']['peer_id']
        R_args['v'] = 5.38
        try:
            try:
                tag = args['tag'].replace(' ', '').split(';')
                func = 'search'
            except:
                tag = args['user'].replace(" ", "")
                func = 'user'
        except:
            return False
        try:
            n = int(args['n'])
        except:
            n = 5
        if func == "search":
            imgs, _ = D_A.search(tag)
            R_args['message'] = 'Фото по тэгу {} с сайта Deviantart'.format(' '.join(tag))
        elif func == 'user':
            imgs, _ = D_A.user(tag)
            R_args['message'] = 'Фото от пользователя {} с сайта Deviantart'.format(tag)
        print(imgs)
        atts = self.UploadPhoto(imgs[:n])
        R_args['attachment'] = atts
        # self.Reply(self.UserApi,R_args)
        args['forward_messages'] = args['data']['message_id']
        self.Replyqueue.put(R_args)
        return True

    def e926(self, args):
        R_args = {}
        print(args)
        R_args['peer_id'] = args['args']['peer_id']
        tags = args['tags'].split(';')
        n = int(args['n'])
        try:
            page = int(args['page'])
        except:
            page = 1
        try:
            sort_ = args['sort'].replace(' ', '')
        except:
            sort_ = 'random'

        imgs = e6.getSafe(tags=tags, n=n, page=page, sort_=sort_)
        atts = self.UploadPhoto(imgs)


        R_args['attachment'] = atts
        R_args['v'] = 5.38
        R_args['message'] = 'Вот картиночки по твоему запросу:\n'
        for img in imgs:
            R_args['message'] += '{}\n'.format(img)
        # self.Reply(self.UserApi, R_args)
        args['forward_messages'] = args['data']['message_id']
        self.Replyqueue.put(R_args)

        return True

    def YT(self, args):
        try:
            text = args['text'].split(' ')
        except:
            pass
        m = ""
        R_args = {}
        R_args['v'] = 5.38
        R_args['peer_id'] = args['data']['peer_id']
        videos, titles = YT_.search(text)
        for i in range(len(titles)):
            m += "{}.{}\n".format(i, titles[i])
        R_args['message'] = m
        self.Replyqueue.put(R_args)
        ans = self.WaitForMSG(5, args)
        R_args['message'] = videos[ans]
        R_args['forward_messages'] = args['data']['message_id']
        self.Replyqueue.put(R_args)

        return True
        # YT_.search()

    def WaitForMSG(self, timer, args):
        print('WFM', args)
        user = args['data']['user_id']
        peer_id = args['data']['peer_id']
        for _ in range(timer):
            sleep(3)
            hist = self.UserApi.messages.getHistory(**{"peer_id": peer_id, "user_id": user, "count": 50, 'v': 5.38})
            for msg in hist['items']:
                # print(msg)
                # print(int(msg['from_id'])==int(user),';',msg['date']==args['data']['date'])
                try:
                    if (int(msg['from_id']) == int(user)) and (msg['body'].startswith('!')):
                        if msg['date'] == args['data']['date']:
                            break
                        # print(msg)
                        # print(msg['body'][1:])
                        ans = int(msg['body'][1:])
                        return ans

                except:
                    continue

    def Likes(self, args):
        R_args = {}
        R_args['forward_messages'] = args['data']['message_id']
        R_args['v'] = 5.38
        R_args['peer_id'] = args['data']['peer_id']
        owner_id = int(args['id'])
        user = self.GetUserNameById(owner_id)
        try:
            n = int(args['n'])
        except:
            n = 5
        try:
            count = int(args['count'])
        except:
            count = 20
        b = 0
        Wall = self.UserApi.wall.get(owner_id=owner_id, count=count, v=5.53)
        print('Wall hooked')
        sleep(1)
        for post in Wall['items']:
            L = int(
                self.UserApi.likes.isLiked(owner_id=post['owner_id'], type='post', item_id=post['id'], v=5.53)['liked'])
            if L == 0:
                print(b)
                if b == n:
                    break
                b += 1
                a = self.UserApi.likes.add(owner_id=post['owner_id'], type='post', item_id=post['id'], v=5.53)
            sleep(1)
        R_args['message'] = 'Пользователю {} пролайкано {} постов'.format(
            ' '.join([user['first_name'], user['last_name']]), b)
        self.Replyqueue.put(R_args)
        return True
    def CheckForCommands(self):
        while True:
            print('Unfinished Check tasks:', self.Checkqueue.unfinished_tasks)
            sleep(1)
            data = self.Checkqueue.get()
            user = self.GetUserNameById(data['user_id'])

            try:
                self.toPrint = user['first_name'] + ' ' + user['last_name'] + " : " + str(
                    data['message']) + '\n' + 'message_id : ' + str(data['message_id']) + '  peer_id : ' + str(
                    data['peer_id'])
                print(self.toPrint)
            except:
                pass

            Commands = {
                '!пост': [self.MakePost, ['admin', 'editor', 'moderator'], "постит в группе ваш текст"],
                '!бан': [self.BanUser, ['admin', 'editor', 'moderator'], ',Банит'],
                '!музыка': [self.Music, ['admin', 'editor', 'moderator', 'user'], "Ищет музыку"],
                '!e621': [self.e621, ['admin', 'editor', 'moderator'], "Ищет пикчи на e621"],
                '!e926': [self.e926, ['admin', 'editor', 'moderator', 'user'], "Ищет пикчи на e926"],
                '!d_a': [self.D_A, ['admin', 'editor', 'moderator', 'user'], "Ищет пикчи на DA"],
                '!yt': [self.YT, ['admin', 'editor', 'moderator', 'user'], "Ищет видео на Ютубе"],
                # 'фото': [self.UploadPhoto, ['admin', 'editor', 'moderator','user']],
                '!добавить': [self.AddUser, ['admin'], "Не для вас"],
                '!likes': [self.Likes, ['admin'], "Тоже не для вас"],
                '!rss': [self.GetRss, ['admin', 'editor', 'moderator', 'user'], "РСС парсит"]
            }
            CommandDict = {}
            args = {}
            if data != '':

                try:
                    if data['message'].startswith('!помощь'):
                        Command_ = data['message'].split(':')
                        args['peer_id'] = data['peer_id']
                        args['v'] = 5.38
                        args['message'] = Commands[Command_[1]][2]
                        self.Replyqueue.put(args)
                        continue
                    if '!команды' in data['message']:
                        args['peer_id'] = data['peer_id']
                        args['v'] = 5.38
                        a = ""
                        for command in Commands.keys():
                            a += 'Команда: {},{}\n'.format(command, Commands[command][2])
                        args['message'] = str(a)
                        # self.Reply(self.UserApi, args)
                        self.Replyqueue.put(args)
                        continue
                    if data['message'].startswith('!'):
                        args['peer_id'] = data['peer_id']
                        args['v'] = 5.38
                        comm = data["message"]
                        comm = comm.split("<br>")
                        User_group = 'user'
                        for C in comm[1:]:
                            C = C.split(":")
                            CommandDict[C[0].replace(" ", "").lower()] = ':'.join(C[1:])
                        Command = comm[0].replace(" ", "").lower()
                        print('Command - ', Command)
                        CommandDict['args'] = args
                        CommandDict['data'] = data
                        print(CommandDict)
                        if Command in Commands:

                            for group in self.UserGroups.keys():
                                if data['user_id'] in self.UserGroups[group]:
                                    print('user check - True')
                                    User_group = group
                                    print('User group - ', User_group)
                                    break
                                elif data['user_id'] not in self.UserGroups[group]:

                                    User_group = 'user'
                                    print('User group - ', User_group)


                            Command_Users = Commands[Command][1]
                            print('Users groups for command -', Command, ' - ', Command_Users)
                            print('access check of user - ', User_group, ' - ', User_group in Command_Users)
                            access = User_group in Command_Users
                            if access:
                                args['message'] = "Выполняю, подождите"
                                self.Replyqueue.put(args)
                                ret = self.ExecCommand(Commands[Command][0], CommandDict)
                            elif not access:
                                ret = False
                                args['message'] = "Недостаточно прав"
                                self.Replyqueue.put(args)

                            if ret == True:
                                self.Checkqueue.task_done()
                                continue
                                args['message'] = "Выполнено"
                                self.Replyqueue.put(args)
                                self.Checkqueue.task_done()
                                continue
                            else:
                                args['message'] = "Не удалось выполнить"
                                self.Replyqueue.put(args)
                        else:
                            if (data['message'][1:]).isdigit():
                                continue
                            args['message'] = "Команда не распознана"
                            self.Replyqueue.put(args)
                    if (self.MyName['first_name'].lower() in data['message'].lower()):

                        if self.hello.search(data['message'], re.IGNORECASE):
                            args['peer_id'] = data['peer_id']
                            args['v'] = 5.38
                            replies = ["Здравствуй {}", "Хай {}", "Здравия {}", "привет {}"]
                            msg = random.choice(replies)

                            while self.oldMsg == msg:
                                msg = random.choice(replies)

                            args['message'] = msg.format(user['first_name'])
                            # self.Reply(self.UserApi, args)
                            self.Replyqueue.put(args)
                            self.oldMsg = msg
                        elif (',котики').lower().replace(' ', '') in data['message'].lower().replace(' ', ''):
                            args['peer_id'] = data['peer_id']
                            args['v'] = 5.38
                            args['message'] = 'мимими, '
                            Kotik = mimimi()
                            att = self.UploadPhoto(Kotik)
                            args['attachment'] = att
                            # self.Reply(self.UserApi, args)
                            self.Replyqueue.put(args)
                        elif ',где'.lower().replace(' ', '') in data['message'].lower().replace(' ', ''):
                            args['peer_id'] = data['peer_id']
                            args['v'] = 5.38
                            args['forward_messages'] = data['message_id']
                            replies = ["Под столом", "На кровати", "За спиной", "На столе"]
                            msg = random.choice(replies)

                            while self.oldMsg == msg:
                                msg = random.choice(replies)

                            args['message'] = msg
                            # self.Reply(self.UserApi, args)
                            self.Replyqueue.put(args)
                            self.oldMsg = msg
                        elif ',кто'.lower().replace(' ', '') in data['message'].lower().replace(' ', ''):
                            args['peer_id'] = data['peer_id']
                            args['v'] = 5.38
                            args['forward_messages'] = data['message_id']
                            if int(data['peer_id']) <= 2000000000:
                                args['message'] = "Это точно ты"
                                self.Replyqueue.put(args)
                            else:
                                chat = int(data['peer_id']) - 2000000000
                                users = self.UserApi.messages.getChatUsers(chat_id=chat, fields='nickname', v=5.38)
                                user = random.choice(users)
                                if user['id'] == self.MyUId:
                                    args['message'] = 'Определённо я'
                                    self.Replyqueue.put(args)
                                    continue
                                name = '{} {}'.format(user['first_name'], user['last_name'])
                                replies = ["Определённо это {}", "Это точно {}", "Я уверен, что это {}", "Это {}"]
                                msg = random.choice(replies)

                                while self.oldMsg == msg:
                                    msg = random.choice(replies)

                                args['message'] = msg.format(name)
                                # self.Reply(self.UserApi, args)
                                self.Replyqueue.put(args)
                                self.oldMsg = msg
                        elif ',кого'.lower().replace(' ', '') in data['message'].lower().replace(' ', ''):
                            args['peer_id'] = data['peer_id']
                            args['v'] = 5.38
                            args['forward_messages'] = data['message_id']
                            if int(data['peer_id']) <= 2000000000:
                                args['message'] = "Тебя"
                                self.Replyqueue.put(args)
                            else:
                                chat = int(data['peer_id']) - 2000000000
                                users = self.UserApi.messages.getChatUsers(chat_id=chat, fields='nickname', v=5.38,
                                                                           name_case='acc')
                                user = random.choice(users)
                                if user['id'] == self.MyUId:
                                    args['message'] = 'Определённо меня'
                                    self.Replyqueue.put(args)
                                    continue
                                name = '{} {}'.format(user['first_name'], user['last_name'])
                                replies = ["Определённо {}", "Точно {}", "Я уверен что его -  {}"]
                                msg = random.choice(replies)

                                while self.oldMsg == msg:
                                    msg = random.choice(replies)

                                args['message'] = msg.format(name)
                                # self.Reply(self.UserApi, args)
                                self.Replyqueue.put(args)
                                self.oldMsg = msg
                        elif ',вероятность'.lower().replace(' ', '') in data['message'].lower().replace(' ', ''):
                            args['peer_id'] = data['peer_id']
                            args['v'] = 5.38
                            a = data['message'].split(' ')
                            if 'вероятность' in a[1]:
                                a = a[2:]
                            else:
                                a = a[1:]
                            args['forward_messages'] = data['message_id']
                            msg = "Вероятность того, что {}, равна {}%".format(' '.join(a), randint(0, 100))

                            args['message'] = msg
                            # self.Reply(self.UserApi, args)
                            self.Replyqueue.put(args)

                except Exception as Ex:

                    args['peer_id'] = data['peer_id']
                    args['v'] = 5.38
                    print(Ex.__traceback__)
                    sleep(1)
                    if 'many requests per second' in str(Ex):
                        print('Too many requests per second')
                        # self.Checkqueue.put(data,timeout=5)
                        continue
                    args['message'] = "Не удалось выполнить, ошибка:{} {} ".format(str(Ex), str(Ex.__traceback__))
                    # self.Reply(self.UserApi, args)
                    self.Replyqueue.put(args)

            self.Checkqueue.task_done()

    def getMus(self):
        music = self.UserApi.audio.get(count=6000)
        print(music)

    def LongPool(self, key, server, ts):
        url = 'http://' + server + '?act=a_check&key=' + key + '&ts=' + str(ts) + '&wait=25&mode=2'
        try:

            result = requests.get(url).json()
        except ValueError:
            result = '{ failed: 2}'
        return result

    def GetUserFormMessage(self, message_id):
        sleep(0.25)

        try:
            uid = self.UserApi.messages.getById(message_id=message_id)[1]['uid']
            return uid
        except:
            sleep(1)
            uid = self.UserApi.messages.getById(message_id=message_id)[1]['uid']
            return uid

    def ContiniousMessageCheck(self, server=''):
        print('done')

        while True:
            # print(time.time())
            if (server == ''):
                results = self.UserApi.messages.getLongPollServer()
                key = results['key']
                server = results['server']
                ts = results['ts']
            results = self.LongPool(key, server, ts)
            try:
                ts = results['ts']
            except (KeyError, TypeError):
                key = ''
                server = ''
                ts = ''
                sleep(0.001)
                continue
            try:
                updates = results['updates']
            except (KeyError, TypeError):
                key = ''
                server = ''
                ts = ''
                sleep(0.001)
                continue
            if updates:
                try:
                    s = updates[0]
                except KeyError:
                    continue
                try:
                    code = s[0]
                except KeyError:
                    continue
                if code == 4:
                    try:
                        args = {}
                        message_id = s[1]
                        flags = s[2]
                        from_id = s[3]
                        timestamp = s[4]
                        subject = s[5]
                        text = s[6]
                        args['peer_id'] = from_id
                        args["message"] = text
                        args['message_id'] = message_id
                        args['date'] = timestamp
                        args['user_id'] = self.GetUserFormMessage(message_id)
                        args['v'] = 5.38
                        # user =self.GetUserNameById(args['user_id'])
                        # print(user['first_name'],user['second_name'],' : ',text)
                        # if args['user_id'] != self.MyUId:
                        # GUI.Gui.UpdateGUI(args)
                        if text == '!':
                            continue
                        self.Checkqueue.put(args, timeout=60)
                        #self.CheckForCommands(args)
                        # self.Reply(self.UserApi,args)
                        # return from_id,text,subject
                    except KeyError:
                        continue
                elif code == 8:
                    continue
                    try:
                        user = self.GetUserNameById(s[1] * -1)
                        try:
                            if user['sex'] == 2:
                                sex = 'Вошел'
                            elif user['sex'] == 1:
                                sex = 'Вошла'
                        except:
                            sex = 'Вошло'
                        print(user['first_name'], user['last_name'], ' {} в сеть'.format(sex))
                    except KeyError:
                        continue
                elif code == 9:
                    continue
                    try:

                        user = self.GetUserNameById(s[1] * -1)
                        try:
                            if user['sex'] == 2:
                                sex = 'Вышел'
                            elif user['sex'] == 1:
                                sex = 'Вышла'


                        except:
                            sex = 'Вышло'
                        try:
                            print(user['first_name'], user['last_name'], ' {} из сети'.format(sex))
                        except:
                            print('Что-то пошло не так при выходе из сети')
                    except KeyError:
                        continue
                elif code == 61:
                    continue
                    try:
                        user = self.GetUserNameById(s[1])
                        print(user['first_name'], user['last_name'], 'Набирает сообщение')
                    except:
                        continue
                elif code == 62:
                    continue
                    user = self.GetUserNameById(s[1])

                    arg = {}
                    arg['chat_id'] = s[2]

                    try:
                        chat = self.UserApi.messages.getChat(**arg)
                    except:
                        chat = {}
                        chat['title'] = 'Хз чё, но тута ошибка'

                    try:
                        print(user['first_name'], user['last_name'], 'Набирает сообщение в беседе', chat['title'])
                    except:
                        continue
                try:
                    sflags = ''
                    if flags & 1:
                        sflags = sflags + 'UNREAD '
                    if flags & 2:
                        sflags = sflags + 'OUTBOX '
                    if flags & 4:
                        sflags = sflags + 'REPLIED '
                    if flags & 8:
                        sflags = sflags + 'IMPORTANT '
                    if flags & 16:
                        sflags = sflags + 'CHAT '
                    if flags & 32:
                        sflags = sflags + 'FRIEND '
                    if flags & 64:
                        sflags = sflags + 'SPAM '
                    if flags & 128:
                        sflags = sflags + 'DELETED '
                    if flags & 256:
                        sflags = sflags + 'FIXED '
                    if flags & 512:
                        sflags = sflags + 'MEDIA '

                except:
                    continue

    def status(self):
        self.UserApi.status.set(text=self.OldStat)

A = VK_Bot()
# print(A.CheckWall("5nights"))
# A.ClearPosts()
atexit.register(A.status)
A.ContiniousMessageCheck()
# print(A.getMus())
# print(A.GetChats())
