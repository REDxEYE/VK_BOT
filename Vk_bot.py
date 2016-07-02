import importlib
import json
import logging
import logging.config
import os
from datetime import datetime, timedelta
from math import ceil
from time import sleep

import requests
import vk
from vk.exceptions import VkAuthError, VkAPIError
from vk.logs import LOGGING_CONFIG
from vk.utils import stringify_values, json_iter_parse, LoggingSession, str_type

V = 1.5
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



class VK_Bot(vk.api.Session):
    def __init__(self):
        print('Loading')
        self.LoadConfig()
        self.Group = self.Settings['Group']
        self.GroupDomain = self.Settings['Domain']
        self.GroupAccess_token = self.Settings['GroupAccess_token']
        self.UserAccess_token = self.Settings['UserAccess_token']
        self.UserSession = vk.SessionCapchaFix(access_token=self.UserAccess_token)
        self.GroupSession = vk.SessionCapchaFix(access_token=self.GroupAccess_token)
        self.UserApi = vk.API(self.UserSession)
        self.GroupApi = vk.API(self.GroupSession)
        self.MyUId = self.UserApi.users.get()[0]['uid']

    def get_captcha_key(self, captcha_image_url):

        importlib.reload(vk)
        print(captcha_image_url)
        cap = input()
        return cap
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
        sleep(0.01)
        User = self.UserApi.users.get(user_ids=Id)[0]
        return User

    def GetCommentsFromPost(self, GroupId, PostId, count):
        comments = []
        комментарии = []
        for _ in range(0, ceil(count / 100)):
            sleep(0.25)
            for Com in self.UserApi.wall.getComments(owner_id=GroupId, post_id=PostId, count=100)[1:]:
                comments.append(Com)
        for comment in comments:
            комментарии.append([self.GetUserNameById(comment['uid']), comment['text']])
        Вывод = ""
        for комментарий in комментарии:
            Вывод += комментарий[0] + " : " + комментарий[1] + "\n"
        return Вывод

    def CheckWall(self, GroupDomain):
        # bans = api.groups.getBanned(group_id="75615891")
        self.Wall = self.UserApi.wall.get(domain=GroupDomain, filter="others", count=10)
        self.posts = self.Wall[1:]
        Вывод = ""
        # print(self.posts[1])
        for I in self.posts:
            # Комментарии = self.GetCommentsFromPost(I['to_id'],I['id'],I['reply_count'])
            # print(I)
            sleep(0.25)
            self.Дата = datetime.fromtimestamp(I['date'])
            self.LikeCount = I['likes']['count']
            # print("Кол-во лайков: ",LikeCount)
            if I['text']:
                Текст = I['text']
            else:
                Текст = "Без текста"
            ФиоПользователя = self.GetUserNameById(I["from_id"])
            IdПользователя = I["from_id"]
            Вывод += ФиоПользователя + " : " + str(IdПользователя) + "\n"
            Вывод += Текст + '\n'
            Вывод += "Кол-во лайков: " + str(self.LikeCount) + "\n"
            Вывод += "Дата: " + str(self.Дата) + "\n"
            # Вывод += "Комментарии:\n" +Комментарии+"\n"
            Вывод += '\n\n'
        return Вывод

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
            self.Settings = settings["settings"]

    def SaveConfig(self):
        path = getpath()
        with open(path + '/settings.json', 'w') as config:
            json.dump(self.UserGroups, config)

    def AddUser(self, args):
        print(args)
        if "группа" in args:
            Group = args['группа']
        else:
            Group = "user"
        if 'id' in args:
            if Group in self.UserGroups:
                Ids = self.UserGroups[Group]
                Ids.append(args['id'])
                self.UserGroups[Group] = Ids
            else:
                self.UserGroups[Group] = [int(args['id'])]

            self.SaveConfig()
            return True
        else:
            return False

    def ExecCommand(self, command, args):
        return command(args)

    def Reply(self, api, args):
        print('Reply:', args)
        sleep(0.1)
        try:
            api.messages.send(**args)
        except:
            pass

    def CheckForCommands(self, data="", StartCommand="!Команда", count=10):
        print(data)
        Commands = {
            'пост': [self.MakePost, ['admin', 'editor', 'moderator']],
            'бан': [self.BanUser, ['admin', 'editor', 'moderator']],
            'добавить': [self.AddUser, ['admin']],
        }
        CommandDict = {}
        args = {}
        if data == '':

            Dialogs = self.GroupApi.messages.getDialogs(count=count)

            for Dialog in Dialogs[1:]:
                # print(Dialog)
                if StartCommand in Dialog['body']:

                    user_id = Dialog["uid"]
                    args['user_id'] = user_id
                    args['peer_id'] = self.Group
                    args['v'] = '5.38'
                    User_group = 'user'
                    comm = Dialog["body"]
                    comm = comm.split("<br>")
                    for C in comm:
                        C = C.split(":")
                        CommandDict[C[0].replace(" ", "").lower()] = C[1]
                    print(CommandDict)
                    if CommandDict["!команда"].replace(" ", "") in Commands:
                        for group in self.UserGroups:
                            if int(user_id) in self.UserGroups[group]:
                                User_group = group
                        if User_group in Commands[CommandDict["!команда"].replace(" ", "")][1] or 'all' in \
                                Commands[CommandDict["!команда"].replace(" ", "")][1]:
                            ret = self.ExecCommand(Commands[CommandDict["!команда"].replace(" ", "")][0], CommandDict)
                        else:
                            ret = False
                            args['message'] = "!Недостаточно прав"
                            self.Reply(self.GroupApi, args)
                            # self.GroupApi.messages.send(user_id=user_id, peer_id=self.Group, message="!Недостаточно прав",v="5.38")
                        if ret == True:
                            args['message'] = "!Выполннено"
                            self.Reply(self.GroupApi, args)
                            # self.GroupApi.messages.send(user_id=user_id, peer_id=self.Group, message="!Выполннено",v="5.38")
                        else:
                            args['message'] = "!Не удалось выполнить"
                            self.Reply(self.GroupApi, args)
                            # self.GroupApi.messages.send(user_id=Dialog["uid"], peer_id=self.Group, message="!Не удалось выполнить",v="5.38")
                    else:
                        args['message'] = "!Команда не распознана"
                        self.Reply(self.GroupApi, args)
                        # self.GroupApi.messages.send(user_id=Dialog["uid"], peer_id=self.Group,message="Команда не распознана", v="5.38")
        if data != '':
            if '!Команда' in data['message']:
                args['peer_id'] = data['peer_id']
                args['v'] = 5.38
                comm = data["message"]
                comm = comm.split("<br>")
                for C in comm:
                    C = C.split(":")
                    CommandDict[C[0].replace(" ", "").lower()] = C[1]
                if CommandDict["!команда"].replace(" ", "") in Commands:
                    for group in self.UserGroups:
                        if int(user_id) in self.UserGroups[group]:
                            User_group = group
                    if User_group in Commands[CommandDict["!команда"].replace(" ", "")][1] or 'all' in \
                            Commands[CommandDict["!команда"].replace(" ", "")][1]:
                        ret = self.ExecCommand(Commands[CommandDict["!команда"].replace(" ", "")][0], CommandDict)
                    else:
                        ret = False
                        args['message'] = "Недостаточно прав"
                        self.Reply(self.UserApi, args)
                        # self.GroupApi.messages.send(user_id=user_id, peer_id=self.Group, message="!Недостаточно прав",v="5.38")
                    if ret == True:
                        args['message'] = "Выполннено"
                        self.Reply(self.UserApi, args)
                        # self.GroupApi.messages.send(user_id=user_id, peer_id=self.Group, message="!Выполннено",v="5.38")
                    else:
                        args['message'] = "Не удалось выполнить"
                        self.Reply(self.UserApi, args)
                        # self.GroupApi.messages.send(user_id=Dialog["uid"], peer_id=self.Group, message="!Не удалось выполнить",v="5.38")
                else:
                    args['message'] = "Команда не распознана"
                    self.Reply(self.UserApi, args)
                    # self.GroupApi.messages.send(user_id=Dialog["uid"], peer_id=self.Group,message="Команда не распознана", v="5.38")
            if (self.GetUserNameById(self.MyUId)['first_name'] + ',привет').lower().replace(' ', '') in data[
                'message'].lower().replace(' ', ''):
                args['peer_id'] = data['peer_id']
                args['v'] = 5.38
                args['message'] = 'Здравствуй, ' + self.GetUserNameById(data['user_id'])['first_name']
                self.Reply(self.UserApi, args)


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
        uid = self.UserApi.messages.getById(message_id=message_id)[1]['uid']
        return uid

    def ContiniousMessageCheck(self, server=''):

        while True:

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
                        args['user_id'] = self.GetUserFormMessage(message_id)
                        args['v'] = 5.38
                        # user =self.GetUserNameById(args['user_id'])
                        # print(user['first_name'],user['second_name'],' : ',text)
                        if args['user_id'] != self.MyUId:
                            self.CheckForCommands(args)
                            # self.Reply(self.UserApi,args)
                            # return from_id,text,subject
                    except KeyError:
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
                    pass


A = VK_Bot()
# print(A.CheckWall("5nights"))
# A.ClearPosts()
A.ContiniousMessageCheck()
# print(A.getMus())
# print(A.GetChats())
