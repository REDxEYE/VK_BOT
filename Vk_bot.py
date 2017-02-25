import calendar
import datetime
import json
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
import traceback
from math import *
from time import sleep
from tkinter import ttk
from urllib.request import urlopen

import aiml
import giphypop
import requests
from PIL import ImageTk
from vk import *

import DA_Api as D_A
import Vk_bot_RssModule
import YT_Api as YT_
import e621_Api as e6
from GlitchLib import *
from Mimimi_Api import *
from PIL_module import *
from filters import *
from tempfile_ import *


def getpath():
    return os.path.dirname(os.path.abspath(__file__))


def prettier_size(n, pow=0, b=1024, u='B', pre=[''] + [p + 'i' for p in 'KMGTPEZY']):
    r, f = min(int(log(max(n * b ** pow, 1), b)), len(pre) - 1), '{:,.%if} %s%s'
    return (f % (abs(r % (-r - 1)), pre[r], u)).format(n * b ** pow / b ** float(r))
class SessionCapchaFix(Session):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    def get_captcha_key(self, captcha_image_url):
        """
        Default behavior on CAPTCHA is to raise exception
        Reload this in child
        """
        print(captcha_image_url)
        img = urllib.request.Request(captcha_image_url, headers=self.hdr)
        a = TempFile(img, 'jpg', NoCache=True)
        self.popup(img)
        a.rem()
        # cap = input('capcha text:')
        return self.capcha.get()

    def popup(self, img):
        img = Image.open(img)

        self.root = tk.Toplevel()
        img = ImageTk.PhotoImage(image=img)

        Img = tk.Label(self.root)
        Img.pack()
        Img.configure(image=img)
        Img._image_cache = img
        self.capcha = ttk.Entry(self.root)
        self.capcha.pack()
        button = ttk.Button(self.root, command=self.Ret)
        button.pack()
        self.root.mainloop()

    def Ret(self):
        self.root.destroy()


class VK_Bot:
    def __init__(self, debug=False, threads=4, LP_Threads=4):
        self.DEBUG = debug
        self.GUI = threading.Thread(target=self.GUI)
        self.GUI.setDaemon(True)
        self.GUI.start()
        sleep(0.5)
        self.stdout.tag_config("log", foreground="black", font="Arial 10 italic")
        self.stdout.tag_config("message", foreground="black", font="Arial 10 italic")
        self.stdout.tag_config("event", foreground="black", font="Arial 10 italic")
        self.stdout.tag_config("reply", foreground="black", font="Arial 10 italic")
        self.stdout.tag_config("command", foreground="black", font="Arial 10 italic")
        self.stdout.tag_config("error", foreground="black", font="Arial 13 italic")
        self.kernel = aiml.Kernel()
        # if os.path.isfile("bot_brain.brn"):
        #    pass
        #    self.kernel.bootstrap(brainFile="bot_brain.brn")
        # else:
        #    pass
        #    self.kernel.bootstrap(learnFiles="startup.xml")
        #    self.kernel.bootstrap(learnFiles="1.xml")
        #    self.kernel.saveBrain("bot_brain.brn")
        self.kernel.bootstrap(learnFiles="startup.xml")
        self.kernel.bootstrap(learnFiles="1.xml")
        self.kernel.setTextEncoding('utf-8')
        self.hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        self.Longpool = queue.Queue()
        self.Checkqueue = queue.Queue()
        self.Replyqueue = queue.Queue()
        self.LOG('log', "MAIN THREAD", "Loading")
        print('Loading')
        self.LoadConfig()
        if 'namelock' not in self.Settings:
            self.Settings['namelock'] = {}
        self.SaveConfig()
        for _ in range(threads):
            self.t = threading.Thread(target=self.CheckForCommands)
            self.t.setDaemon(True)
            self.t.start()
            print('Поток обработки сообщений создан')
            self.LOG('log', "MAIN THREAD", "Поток обработки сообщений создан")
        for _ in range(LP_Threads):
            self.LP = threading.Thread(target=self.parseLongPool)
            self.LP.setDaemon(True)
            self.LP.start()
            self.LOG('log', "MAIN THREAD", 'Поток обработки лонгпула создан')
            print('Поток обработки лонгпула создан')
        self.y = threading.Thread(target=self.Reply)
        self.y.setDaemon(True)
        self.y.start()

        self.LOG('log', "MAIN THREAD", 'Поток обработки ответов создан')
        print('Поток обработки ответов создан')

        self.Group = self.Settings['Group'] if 'Group' in self.Settings else None
        self.GroupDomain = self.Settings['Domain'] if 'Domain' in self.Settings else None
        self.GroupAccess_token = self.Settings['GroupAccess_token'] if 'GroupAccess_token' in self.Settings else None
        self.UserAccess_token = self.Settings['UserAccess_token']
        self.UserSession = SessionCapchaFix(access_token=self.UserAccess_token)
        self.GroupSession = SessionCapchaFix(
            access_token=self.GroupAccess_token) if self.GroupAccess_token != None else None
        self.UserApi = API(self.UserSession)
        self.GroupApi = API(self.GroupSession) if self.GroupAccess_token != None else None
        self.MyUId = self.UserApi.users.get()[0]['uid']
        self.MyName = self.GetUserNameById(self.MyUId)
        self.hello = re.compile(
            '(прив(|а|ет(|ик)(|ствую))|х(а|е)й|зд((о|а)ров(а|)|ра(е|ь)|вствуй(|те)))|добр(ое|ый) (день|утро|вечер)')
        self.oldMsg = ""
        self.OldStat = self.UserApi.status.get()['text']
        self.UserApi.status.set(text="Bot online")
        self.chatlist = self.UserApi.messages.getDialogs(v=5.60, count=20)
        # self.buildChatlist()
        # friends = self.UserApi.friends.getRequests(v=5.38)['items']
        # for friend in friends:
        #    self.UserApi.friends.add(user_id=friend)
        self.Commands = {
            '!пост': [self.MakePost, ['admin', 'editor', 'moderator'], "постит в группе ваш текст", '', False],
            # '!бан': [self.BanUser, ['admin', 'editor', 'moderator'], 'Банит', '', False],
            '!музыка': [self.Music, ['admin', 'editor', 'moderator', 'user'], 'Ищет музыку',
                        "Ищет музыку, форма запроса:\n!музыка\nимя:НАЗВАНИЕ", True],
            '!e621': [self.e621, ['admin', 'editor', 'moderator'], "Ищет пикчи на e621",
                      "Ищет пикчи на e621, форма запроса:\n"
                      "!e621\n"
                      "tags:тэги через ;\n"
                      "sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n"
                      "n:кол-во артов(максимум 10)\n"
                      "page:страница на которой искать",
                      False],
            '!e926': [self.e926, ['admin', 'editor', 'moderator', 'user'], "Ищет пикчи на e926",
                      "Ищет пикчи на e926, форма запроса:\n"
                      "!e926\n"
                      "tags:тэги через ;\n"
                      "sort:fav_count либо score либо вообще не пишите это, если хотите случайных\n"
                      "n:кол-во артов(максимум 10)\n"
                      "page:страница на которой искать",
                      False],
            '!d_a': [self.D_A, ['admin', 'editor', 'moderator', 'user'], "Ищет пикчи на DA", '', False],
            '!yt': [self.YT, ['admin', 'editor', 'moderator', 'user'], "Ищет видео на Ютубе", '', False],
            '!глюк': [self.Glitch, ['admin', 'editor', 'moderator', 'user'], "Глючная обработка фото", '', False],
            '!сделайглюк': [self.GifFromPhoto, ['admin', 'editor', 'moderator', 'user'],
                            "Создаёт глючную гифку из фото", '', False],
            '!сделайглюкvsh': [self.GifFromPhotoVSH, ['admin', 'editor', 'moderator', 'user'],
                               "Создаёт глючную гифку из фото", '', False],
            '!prism': [self.Prism, ['admin', 'editor', 'moderator', 'user'], "Глючная обработка фото", '', False],
            # 'фото': [self.UploadPhoto, ['admin', 'editor', 'moderator','user']],
            '!добавить': [self.AddUser, ['admin'], "Не для вас", '', False],
            '!likes': [self.Likes, ['admin'], "Тоже не для вас", '', False],
            '!rss': [self.GetRss, ['admin', 'editor', 'moderator', 'user'], "РСС парсит", '', False],
            '!lockname': [self.LockName, ['admin', 'editor', 'moderator', 'user'], "Лочит имя беседы", '', True],
            '!5nights': [self.JoinFiveNigths, ['admin', 'editor', 'moderator', 'user'], "Добавляет в общую беседу", '',
                         True],
            '!roll': [self.rollRows, ['admin', 'editor', 'moderator', 'user'], "сложна объяснить", '', True],
            '!rollrandom': [self.rollRowsrand, ['admin', 'editor', 'moderator', 'user'], "сложна объяснить", '', True],
            '!rollsmart': [self.rollRowssmart, ['admin', 'editor', 'moderator', 'user'], "сложна объяснить", '', True],
            '!чс': [self.Blacklist, ['admin', 'editor', 'moderator'], "Добавляет человека в игнор лист", '',
                    True],
            '!выполни': [self.ExecCode, ['admin', 'editor'], '', "Выполняет код из сообщения\n"
                                                                 "переменная api содержит api пользователя\n"
                                                                 "переменная self - содержит внутренние функции бота",
                         True],
            '!wanted': [self.WantedFunk, ['admin', 'editor', 'moderator', 'user'], "сложна объяснить", '', True],
            '!jontron': [self.JonTronFunk, ['admin', 'editor', 'moderator', 'user'], "сложна объяснить", '', True],
            '!saymax': [self.SayMaxFunk, ['admin', 'editor', 'moderator', ], "сложна объяснить", '', True],
            '!stat': [self.StatComm, ['admin', 'editor', 'moderator', ], "Выводит стату", '', True],
            '!debug': [self.Debug, ['admin', 'editor', 'moderator', ], "Всякая дебажная фигня", '', True],
            '!изгнать': [self.kik, ['admin', 'editor', 'moderator', ], '',
                         "Изгоняет пользователя из беседы, если бот её создатель \n"
                         "!изнать\n"
                         "id: id предателя", True],
        }
        self.UpdateStats()
        #GUI!!!

    def GUI(self):
        self.root = tk.Tk()
        self.stdout = tk.Text(self.root)
        self.stdout.pack()
        self.root.title('Vk bot GUI')
        self.StatsTemplate = "Messages: {}  Commands:{}  Cache:{}"
        self.Stats = ttk.Label(text="")
        self.Stats.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.quit_)
        self.root.mainloop()

    def quit_(self):

        self.root.destroy()
        os._exit(9)

    def SetCurChat(self, event):

        print(self.Chats.get())
        # self.curChar =

    def buildChatlist(self):
        emoji_pattern = re.compile("[\u1F300-\u1F5FF\u1F600-\u1F64F\u1F680-\u1F6FF\u2600-\u26FF\u2700-\u27BF]+",
                                   flags=re.UNICODE)
        self.ChatList = {}
        for chat in self.chatlist['items']:
            if chat['title'] == ' ... ':
                user = self.GetUserNameById(chat['user_id'])
                print(emoji_pattern.findall(user['first_name']))
                print(emoji_pattern.findall(user['last_name']))
                self.ChatList[chat['user_id']] = "{} {}".format(emoji_pattern.sub(r'', user['first_name']),
                                                                emoji_pattern.sub(r'', user[
                                                                    'last_name'])) if user is not None else "ОШИБКА"
            else:
                self.ChatList[chat['chat_id']] = chat['title']
        print(self.ChatList)
        self.Chats = ttk.Combobox(self.root, values=self.ChatList.values())
        self.Chats.bind("<<ComboboxSelected>>", self.SetCurChat)
        self.Chats.pack()

    def UpdateStats(self):
        self.Stats.configure(
            text=self.StatsTemplate.format(self.Stat['messages'], self.Stat['commands'], self.Stat['cache']))
        self.root.after(1000, self.UpdateStats)

    def LOG(self, tag, prefix="UNKNOWN", *text):
        out = ''
        for t in text:
            if isinstance(t, list):
                out += " ".join(t) + "\n"
            if isinstance(t, dict):
                out += str(t) + "\n"
            if isinstance(text, tuple):
                out += str(t) + "\n"
        if not self.DEBUG:
            if tag == ("log" or "command" or "reply"):
                return
        self.stdout.insert(tk.END, '[{}]: '.format(prefix) + out + os.linesep, tag)
        self.stdout.see("end")

    def getinfo(self, command):
        return 'Неправильно оформлен запрос \n' + self.Commands[command][3]

    def kik(self, args):
        R_args = {'v': 5.45, 'peer_id': args['data']['peer_id']}
        user = args['id'] if 'id' in args else None
        if user == None:
            R_args['message'] = args['info']
            self.Replyqueue.put(R_args)
            return True
        name = self.GetUserNameById(user)
        R_args['message'] = "The kickHammer has spoken\n {} has been kicked in the ass".format(
            ' '.join([name['first_name'], name['last_name']]))
        self.UserApi.messages.removeChatUser(v=5.45, chat_id=args['data']['peer_id'] - 2000000000, user_id=user)
        self.Replyqueue.put(R_args)
        return True

    def Debug(self, args):
        R_args = {'v': 5.45, 'peer_id': args['data']['peer_id']}
        msg = "Кол-во команд в обработке: {}\n".format(self.Checkqueue.unfinished_tasks)
        a = []
        for _ in range(self.Checkqueue.unfinished_tasks):

            try:
                a.append(str(self.Checkqueue.get_nowait()))
            except:
                break
        msg += "Дамп очереди: {}\n".format('\n'.join(a))
        msg += "Имя и ID аккаунта: {}".format(self.MyName)
        R_args['message'] = msg

        self.Replyqueue.put(R_args)
        return True

    def GetChatName(self, id):
        url = 'https://api.vk.com/method/{}?{}&access_token={}'.format('messages.getChat', 'chat_id={}'.format(id),
                                                                       self.Settings['UserAccess_token'])
        resp = requests.get(url).json()
        return resp['response']

    def Blacklist(self, args):
        try:
            self.Settings['blacklist'].append(args['id'])
        except:
            self.Settings['blacklist'] = [args['id']]
        self.SaveConfig()
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
        sleep(0.1)
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
            for Com in self.UserApi.wall.getComments(owner_id=GroupId, post_id=PostId, count=100, v=5.60)['items']:
                comments.append(Com)
        for comment in comments:
            comms.append([self.GetUserNameById(comment['id']), comment['text']])
        Out = ""
        for comm in comms:
            try:
                Out += " ".join([comm[0]['first_name'], comm[0]['last_name']]) + " : " + comm[1] + "\n"
            except:
                Out += 'Кто-то вызвавший эксепшен' + " : " + comm[1] + "\n"
        return Out

    def CheckWall(self, GroupDomain):
        # bans = api.groups.getBanned(group_id="75615891")
        self.Wall = self.UserApi.wall.get(domain=GroupDomain, filter="others", count=10)
        self.posts = self.Wall[1:]
        Out = ""
        # print(self.posts[1])
        for post in self.posts:
            # comms = self.GetCommentsFromPost(I['to_id'],I['id'],I['reply_count'])
            # print(I)
            sleep(0.25)
            self.Data = datetime.datetime.fromtimestamp((post['date']))
            self.LikeCount = post['likes']['count']
            # print("Кол-во лайков: ",LikeCount)
            if post['text']:
                Text = post['text']
            else:
                Text = "Без текста"
            FIO = self.GetUserNameById(post["from_id"])
            ID = post["from_id"]
            Out += "{} {}".format(FIO['first_name'], FIO['last_name']) + " : " + str(ID) + "\n"
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




    def generateConfig(self, path):
        token = input('User access token')
        adminid = input('Admin vk id')
        data = {}
        with open(path + '/settings.json', 'w') as config:
            data['users'] = {'admin': [adminid]}
            data['settings'] = {'UserAccess_token': token}
            json.dump(data, config)
    def LoadConfig(self):
        path = getpath()
        if not os.path.exists(path + '/settings.json'):
            self.generateConfig(path)
        with open(path + '/settings.json', 'r') as config:
            settings = json.load(config)
            self.UserGroups = settings["users"]
            try:
                self.Stat = settings["stat"]
            except:
                self.Stat = {}
                self.Stat['messages'] = 0
                self.Stat['commands'] = 0
                self.Stat['cache'] = 0
            self.LOG('log', sys._getframe().f_code.co_name, 'User groups: ', self.UserGroups)
            print('User groups: ', self.UserGroups)
            self.Settings = settings["settings"]
        self.LOG('log', sys._getframe().f_code.co_name, 'Loading config :done')
        print('Loading config :done')
    def SaveConfig(self):
        path = getpath()
        data = {}
        with open(path + '/settings.json', 'w') as config:
            data['users'] = self.UserGroups

            data['stat'] = self.Stat
            #print(self.Stat)
            data['settings'] = self.Settings
            json.dump(data, config)
            # print('Saving config :done')

    def StatComm(self, args):
        R_args = {}
        msg = 'Кол-во обработанных сообщений: {}\nКол-во выполеных команд: {}\nРазмер кэша: {}\n'
        R_args['message'] = msg.format(self.Stat['messages'], self.Stat['commands'], str(
            prettier_size((os.path.getsize(os.path.join(getpath(), 'tmp', 'cache.zip'))))))
        R_args['peer_id'] = args['args']['peer_id']
        R_args['v'] = 5.45
        self.Replyqueue.put(R_args)
        return True

    def AddUser(self, args):
        self.LOG('log', sys._getframe().f_code.co_name, 'Adduser: ', args)
        print('Adduser: ', args)
        if "группа" in args:
            Group = args['группа'].lower()
        else:
            Group = "user"

        if 'id' in args:
            print(Group in self.UserGroups)
            self.LOG('log', sys._getframe().f_code.co_name, Group in self.UserGroups)
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
            MArgs['v'] = 5.45
            self.LOG('log', sys._getframe().f_code.co_name, 'Adduser reply: ', MArgs)
            print('Adduser reply: ', MArgs)
            # self.Reply(self.UserApi, MArgs)
            self.Replyqueue.put(MArgs)
            self.SaveConfig()

            return True
        else:
            return False

    def ExecCommand(self, command, args):
        self.LOG('log', "Command Exec", 'executing command: ', command, ' with args:')
        print('executing command: ', command, ' with args:')
        self.LOG('log', 'Command Exec', args)
        print(args)
        return command(args)

    def GetRss(self, args):
        print('GetRss ', args)
        url = args['url']
        rss = Vk_bot_RssModule.RssParser(url=url)
        news = rss.Parse()[:5]
        # rss = RssBot.Parse()

        for r in news:
            Margs = {}
            Margs['v'] = 5.45
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
            self.Replyqueue.put(Margs)
            sleep(1)
        return True

    def Reply(self):

        while True:
            #print('Reply queue',self.Replyqueue)
            args = self.Replyqueue.get()
            self.Replyqueue.task_done()
            # print('Unfinished Reply tasks:', self.Replyqueue.unfinished_tasks)
            self.LOG('reply', sys._getframe().f_code.co_name, 'Reply:', args)
            print('Reply:', args)
            sleep(1)
            try:

                self.UserApi.messages.send(**args)
            except Exception as Ex:
                self.LOG('error', sys._getframe().f_code.co_name, 'Reply:', "error couldn't send message:", Ex)
                print("error couldn't send message:", Ex)
                try:
                    args['message'] += '\nФлудконтроль:{}'.format(randint(0, 255))
                except:
                    args['message'] = '\nФлудконтроль:{}'.format(randint(0, 255))
                self.Replyqueue.put(args)


    def GetUploadServer(self):
        return self.UserApi.photos.getMessagesUploadServer()

    def UploadPhoto(self, urls):
        atts = []

        if type(urls) != type(['1', '2']):
            urls = [urls]
        i = 0
        for url in urls:
            i += 1
            self.LOG('log', sys._getframe().f_code.co_name, 'Reply:', 'downloading photo№{}'.format(i))
            print('downloading photo№{}'.format(i))
            server = self.GetUploadServer()['upload_url']
            req = urllib.request.Request(url, headers=self.hdr)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            Tmp.cachefile(Tmp.path_)
            args = {}
            args['server'] = server
            self.LOG('log', sys._getframe().f_code.co_name, 'uploading photo №{}'.format(i))
            print('uploading photo №{}'.format(i))
            req = requests.post(server, files={'photo': open(Tmp.file_(), 'rb')})
            self.LOG('log', sys._getframe().f_code.co_name, 'Done')
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

    def UploadFromDisk(self, file):
        self.Stat['cache'] = str(prettier_size((os.path.getsize(os.path.join(getpath(), 'tmp', 'cache.zip')))))
        atts = []
        server = self.GetUploadServer()['upload_url']
        args = {}
        args['server'] = server
        self.LOG('log', sys._getframe().f_code.co_name, 'uploading photo')
        print('uploading photo №')
        req = requests.post(server, files={'photo': open(file, 'rb')})
        self.LOG('log', sys._getframe().f_code.co_name, 'Done')
        print('Done')
        # req = requests.post(server,files = {'photo':img})
        if req.status_code == requests.codes.ok:
            # print('req',req.json())
            try:
                params = {'server': req.json()['server'], 'photo': req.json()['photo'], 'hash': req.json()['hash']}
                photo = self.UserApi.photos.saveMessagesPhoto(**params)[0]
            except:
                pass

        return photo['id']

    def UploadDocFromDisk(self, file):
        atts = []
        server = self.UserApi.docs.getUploadServer()['upload_url']
        args = {}
        args['server'] = server
        name = file.split('/')[-1]
        self.LOG('log', sys._getframe().f_code.co_name, 'uploading file')
        print('uploading file')
        req = requests.post(server, files={'file': open(file, 'rb')})
        self.LOG('log', sys._getframe().f_code.co_name, 'Done')
        print('Done')
        # req = requests.post(server,files = {'photo':img})
        if req.status_code == requests.codes.ok:
            # print('req',req.json())
            params = {'file': req.json()['file'], 'title': name, 'v': 5.53}
            doc = self.UserApi.docs.save(**params)[0]

            return 'doc{}_{}'.format(doc['owner_id'], doc['id']), doc
        return None, None

    def Music(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        name = args['имя'] if 'имя' in args else None
        if name == None:
            R_args['message'] = args['info']
            self.Replyqueue.put(R_args)
            return True
        tracks = self.UserApi.audio.search(q=name)[1:]
        atts = []
        # print(R_args)
        R_args['message'] = 'Песни по запросу {}'.format(name)
        #print(tracks[0])
        for track in tracks:
            #print(track)
            atts.append('audio{}_{}'.format(track['owner_id'], track['aid']))
        # print(atts)
        R_args['attachment'] = atts
        # print('ats',atts)
        # self.Reply(self.UserApi, R_args)
        self.Replyqueue.put(R_args)

        return True
        # print(tracks)

    def e621(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        tags = args['tags'].split(';') if 'tags' in args else None
        if tags == None:
            R_args['message'] = args['info']
            self.Replyqueue.put(R_args)
            return True
        n = int(args['n']) if 'n' in args else 5
        page = int(args['page']) if 'page' in args else 1
        sort_ = args['sort'].replace(' ', '') if 'sort' in args else 'random'
        imgs = e6.get(tags=tags, n=n, page=page, sort_=sort_)
        self.LOG('log', sys._getframe().f_code.co_name, imgs)
        print(imgs)
        atts = self.UploadPhoto(imgs)
        R_args['attachment'] = atts
        R_args['message'] = 'Вот порнушка по твоему запросу, шалунишка...'
        self.Replyqueue.put(R_args)

        return True

    def D_A(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        if ('tag' or 'user') not in args:
            R_args['message'] = args['info']
            self.Replyqueue.put(R_args)
            return True

        tag = args['tag'].replace(' ', '').split(';') if 'tag' in args else args['user'].replace(" ", "")
        func = 'search' if 'tag' in args else 'user'
        n = int(args['n']) if 'n' in args else 5
        if func == "search":
            imgs, _ = D_A.search(tag)
            R_args['message'] = 'Фото по тэгу {} с сайта Deviantart'.format(' '.join(tag))
        elif func == 'user':
            imgs, _ = D_A.user(tag)
            R_args['message'] = 'Фото от пользователя {} с сайта Deviantart'.format(tag)
        self.LOG('log', sys._getframe().f_code.co_name, imgs)
        print(imgs)
        atts = self.UploadPhoto(imgs[:n])
        R_args['attachment'] = atts
        self.Replyqueue.put(R_args)
        return True

    def WantedFunk(self, args):
        args['peer_id'] = args['data']['peer_id']
        args['v'] = 5.45
        atts = args['data']['attachments']
        #print(atts)
        Topost = []
        if len(atts) != 2:
            args['message'] = 'Нужно 2 фотографии'
            self.Replyqueue.put(args)
            return False
        try:

            photo = self.GetBiggesPic(atts[0], args['data']['message_id'])
        except:
            return False
        try:
            photo1 = self.GetBiggesPic(atts[1], args['data']['message_id'])
        except:
            return False
        req = urllib.request.Request(photo, headers=self.hdr)
        req1 = urllib.request.Request(photo1, headers=self.hdr)
        img = urlopen(req).read()
        img1 = urlopen(req1).read()
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        Wanted(Tmp.path_, Tmp1.path_)
        att = self.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        args['attachment'] = Topost
        self.Replyqueue.put(args)
        return True

    def JonTronFunk(self, args):
        args['peer_id'] = args['data']['peer_id']
        args['v'] = 5.45
        atts = args['data']['attachments']
        #print(atts)
        Topost = []

        try:

            photo = self.GetBiggesPic(atts[0], args['data']['message_id'])
            req = urllib.request.Request(photo, headers=self.hdr)

            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            Tmp.cachefile(Tmp.path_)
            JonTron(Tmp.path_)
            att = self.UploadFromDisk(Tmp.path_)

            Tmp.rem()
        except:
            text = args['text'] if 'text' in args else 'Meh...'
            size = args['size'] if 'size' in args else 120
            font = args['font'] if 'font' in args else 'times.ttf'
            x = int(args['x']) if 'x' in args else 100
            y = int(args['y']) if 'y' in args else 150
            if text == None:
                return False
            _path = textPlain(text, size, font, x, y, 512, 512)
            JonTron(_path)

            att = self.UploadFromDisk(_path)
            os.remove(_path)
            del _path
        Topost.append(att)
        args['attachment'] = Topost
        self.Replyqueue.put(args)
        return True

    def SayMaxFunk(self, args):
        args['peer_id'] = args['data']['peer_id']
        args['v'] = 5.45
        atts = args['data']['attachments']
        #print(atts)
        Topost = []

        try:

            photo = self.GetBiggesPic(atts[0], args['data']['message_id'])
            req = urllib.request.Request(photo, headers=self.hdr)

            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')

            SayMax(Tmp.path_)
            Tmp.cachefile(Tmp.path_)
            att = self.UploadFromDisk(Tmp.path_)
            Tmp.rem()
        except:
            text = args['text'] if 'text' in args else 'кок'
            size = args['size'] if 'size' in args else 300
            font = args['font'] if 'font' in args else 'times.ttf'
            x = int(args['x']) if 'x' in args else 250
            y = int(args['y']) if 'y' in args else 200
            if text == None:
                return False
            _path = textPlain(text, size, font, x, y, 1280, 720)
            SayMax(_path)
            att = self.UploadFromDisk(_path)
            os.remove(_path)
            del _path
        Topost.append(att)

        args['attachment'] = Topost
        self.Replyqueue.put(args)
        return True
    def e926(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        tags = args['tags'].split(';') if 'tags' in args else None
        if tags == None:
            R_args['message'] = args['info']
            self.Replyqueue.put(R_args)
            return True
        n = int(args['n']) if 'n' in args else 5
        page = int(args['page']) if 'page' in args else 1
        sort_ = args['sort'].replace(' ', '') if 'sort' in args else 'random'
        imgs = e6.getSafe(tags=tags, n=n, page=page, sort_=sort_)
        self.LOG('log', sys._getframe().f_code.co_name, imgs)
        atts = self.UploadPhoto(imgs)
        R_args['attachment'] = atts
        R_args['message'] = 'Вот картиночки по твоему запросу:\n'
        for img in imgs:
            R_args['message'] += '{}\n'.format(img)
        # self.Reply(self.UserApi, R_args)
        args['forward_messages'] = args['data']['message_id']
        self.Replyqueue.put(R_args)

        return True

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

    def ExecCode(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        code = self.html_decode(args['data']['message'])
        code = '\n'.join(code.split('<br>')[1:]).replace('|', '  ')
        a = compile(code, '<string>', 'exec')
        l = {'api': self.UserApi, 'self': self}
        g = {}
        exec(a, g, l)
        R_args['message'] = str(l['out']) if 'out' in l else 'Выполнил'
        self.Replyqueue.put(R_args)
        return True

    def YT(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        text = args['text'].split(' ') if 'text' in args else None
        if text == None:
            R_args['message'] = args['info']
            return False
        R_args['message'] = "Временно не работает"
        self.Replyqueue.put(R_args)
        return True
        m = ""
        videos, titles = YT_.search(text)
        for i in range(len(titles)):
            m += "{}.{}\n".format(i, titles[i])
        R_args['message'] = m
        self.Replyqueue.put(R_args)
        ans = self.WaitForMSG(5, args)
        R_args['message'] = videos[ans]
        self.Replyqueue.put(R_args)
        return True

    def WaitForMSG(self, timer, args):
        self.LOG('log', sys._getframe().f_code.co_name, 'WFM', args)
        print('WFM', args)
        try:
            user = args['data']['user_id']
            peer_id = args['data']['peer_id']
            old = True
        except:
            user = args['user_id']
            peer_id = args['peer_id']
            old = False
        for _ in range(timer):
            sleep(3)
            hist = self.UserApi.messages.getHistory(**{"peer_id": peer_id, "user_id": user, "count": 50, 'v': 5.38})

            for msg in hist['items']:
                try:

                    if (int(msg['from_id']) == int(user)) and (re.match(r'\d+$', msg['body'])):
                        if old:
                            if msg['date'] == args['data']['date']:
                                break
                        else:
                            if msg['date'] == args['date']:
                                self.LOG('log', sys._getframe().f_code.co_name, 'Дошел до старого сообщения')
                                print('Дошел до старого сообщения')
                                break


                        ans = int(msg['body'])
                        self.LOG('log', sys._getframe().f_code.co_name, msg['body'])
                        print(msg['body'])
                        return ans

                except:
                    continue

    def Likes(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        owner_id = int(args['id']) if 'id' in args else None
        if owner_id == None:
            R_args['message'] = args['info']
            self.Replyqueue.put(R_args)
            return True
        user = self.GetUserNameById(owner_id)
        n = int(args['n']) if 'n' in args else 5
        count = int(args['count']) if 'count' in args else 20
        b = 0
        Wall = self.UserApi.wall.get(owner_id=owner_id, count=count, v=5.53)
        self.LOG('log', sys._getframe().f_code.co_name, 'Wall hooked')
        print('Wall hooked')
        sleep(1)
        for post in Wall['items']:
            L = int(
                self.UserApi.likes.isLiked(owner_id=post['owner_id'], type='post', item_id=post['id'], v=5.53)['liked'])
            if L == 0:
                #print(b)
                if b == n:
                    break
                b += 1
                a = self.UserApi.likes.add(owner_id=post['owner_id'], type='post', item_id=post['id'], v=5.53)
            sleep(1)
        R_args['message'] = 'Пользователю {} пролайкано {} постов'.format(
            ' '.join([user['first_name'], user['last_name']]), b)
        self.Replyqueue.put(R_args)
        return True

    def Glitch(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        sigma = int(args['sigma']) if 'sigma' in args else 5
        iter = int(args['iter']) if 'iter' in args else 150
        size = int(args['size']) if 'size' in args else 32
        Glitch_ = bool(args['color']) if 'color' in args else True
        random_ = bool(args['rand']) if 'rand' in args else True
        atts = self.UserApi.messages.getById(message_id=args['data']['message_id'])[1]['attachments']
        atts = atts[1]['attachments'] if atts[1]['attachments'] else None
        if atts == None:
            R_args['message'] = args['info']
            self.Replyqueue.put(Random)
            return True

        Topost = []
        for att in atts:
            if att['type'] == 'photo':
                try:
                    photo = att['photo']['src_xxxbig']
                except:
                    try:
                        photo = ['photo']["src_xxbig"]
                    except:
                        try:
                            photo = att['photo']["src_xbig"]
                        except:
                            try:
                                photo = att['photo']["src_big"]
                            except:
                                return False

                req = urllib.request.Request(photo, headers=self.hdr)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg')
                Glitch(file=Tmp.path_, sigma=sigma, blockSize=size, iterations=iter, random_=random_, Glitch_=Glitch_)
                Tmp.cachefile(Tmp.path_)
                att = self.UploadFromDisk(Tmp.path_)
                Topost.append(att)
                Tmp.rem()

        for att in atts:
            if att['type'] == 'doc':
                try:
                    gif = att['doc']['url']
                except:
                    return False
                req = urllib.request.Request(gif, headers=self.hdr)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'gif')
                file = GlitchGif(Tmp.path_, sigma=sigma, blockSize=size, iterations=iter, random_=random_,
                                 Glitch_=Glitch_)
                doc, t = self.UploadDocFromDisk(file)
                Tmp.rem()
                os.remove(file)
                Topost.append(doc)
        R_args['message'] = ':D'
        R_args['attachment'] = Topost

        self.Replyqueue.put(R_args)
        return True

    def GifFromPhoto(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        sigma = int(args['sigma']) if 'sigma' in args else 5
        iter = int(args['iter']) if 'iter' in args else 150
        size = int(args['size']) if 'size' in args else 32
        Glitch_ = bool(args['color']) if 'color' in args else True
        random_ = bool(args['rand']) if 'rand' in args else True
        len_ = int(args['len']) if 'len' in args else 60
        atts = self.UserApi.messages.getById(message_id=args['data']['message_id'])[1]['attachments']
        Topost = []
        for att in atts:
            if att['type'] == 'photo':
                try:
                    photo = att['photo']['src_xxxbig']
                except:
                    try:
                        photo = ['photo']["src_xxbig"]
                    except:
                        try:
                            photo = att['photo']["src_xbig"]
                        except:
                            try:
                                photo = att['photo']["src_big"]
                            except:
                                return False

                req = urllib.request.Request(photo, headers=self.hdr)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg')
                file = MakeGlitchGif(image=Tmp.path_, len_=len_, sigma=sigma, blockSize=size, iterations=iter,
                                     random_=random_, Glitch_=Glitch_)
                doc, t = self.UploadDocFromDisk(file)
                Tmp.cachefile(file)
                os.remove(file)
                Topost.append(doc)
                Tmp.rem()

        R_args['attachment'] = Topost
        R_args['message'] = ':D'
        self.Replyqueue.put(R_args)
        return True

    def GifFromPhotoVSH(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        sigma = int(args['sigma']) if 'sigma' in args else 5
        iter = int(args['iter']) if 'iter' in args else 150
        size = int(args['size']) if 'size' in args else 32
        Glitch_ = bool(args['color']) if 'color' in args else True
        random_ = bool(args['rand']) if 'rand' in args else True
        len_ = int(args['len']) if 'len' in args else 60
        atts = self.UserApi.messages.getById(message_id=args['data']['message_id'])[1]['attachments']
        Topost = []
        for att in atts:
            if att['type'] == 'photo':
                try:
                    photo = att['photo']['src_xxxbig']
                except:
                    try:
                        photo = ['photo']["src_xxbig"]
                    except:
                        try:
                            photo = att['photo']["src_xbig"]
                        except:
                            try:
                                photo = att['photo']["src_big"]
                            except:
                                return False

                req = urllib.request.Request(photo, headers=self.hdr)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg')
                file = MakeGlitchGifVSH(image=Tmp.path_, len_=len_, sigma=sigma, blockSize=size, iterations=iter,
                                        random_=random_, Glitch_=Glitch_)
                Tmp.cachefile(file)
                doc, t = self.UploadDocFromDisk(file)
                os.remove(file)
                Topost.append(doc)
                Tmp.rem()

        R_args['attachment'] = Topost
        R_args['message'] = ':D'
        self.Replyqueue.put(R_args)
        return True

    def LockName(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        id = str(args['data']['peer_id'])
        if id in self.Settings['namelock']:

            self.Settings['namelock'][id] = [args['data']['subject'], not self.Settings['namelock'][id][1]]

        else:
            self.Settings['namelock'][id] = [args['data']['subject'], True]
        if self.Settings['namelock'][id][1]:
            R_args['message'] = 'Смена названия беседы запрещена'
            self.Replyqueue.put(R_args)
        else:
            R_args['message'] = 'Смена названия беседы разрешена'
            self.Replyqueue.put(R_args)
        self.SaveConfig()
        return True

    def JoinFiveNigths(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        are_friend = self.UserApi.friends.areFriends(user_ids=[args['data']['user_id']])[0]['friend_status']
        if int(are_friend) == 3:
            ans = self.UserApi.messages.addChatUser(chat_id=13, user_id=args['data']['user_id'])

            if int(ans) != 1:
                R_args['message'] = 'Ошибка добавления'
            return True

        else:
            f = int(self.UserApi.friends.add(user_id=args['data']['user_id'], text='Что б добавить в беседу'))
            if f == 1 or f == 2:

                ans = self.UserApi.messages.addChatUser(chat_id=13, user_id=args['data']['user_id'])
                R_args['message'] = 'Примите завяку и снова напишите !5nights'
                if int(ans) != 1:
                    R_args['message'] = 'Ошибка добавления'

            else:
                R_args['message'] = 'Не могу добавить вас в друзья, а значит и не могу добавить в беседу'
            self.Replyqueue.put(R_args)
            return True

    def Prism(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        att = self.UserApi.messages.getById(message_id=args['data']['message_id'])[1]['attachments'][0]['photo']
        try:
            photo = att['src_xxxbig']
        except:
            try:
                photo = att["src_xxbig"]
            except:
                try:
                    photo = att["src_xbig"]
                except:
                    try:
                        photo = att["src_big"]
                    except:
                        return False

        req = urllib.request.Request(photo, headers=self.hdr)
        img = urlopen(req).read()
        Tmp = TempFile(img, 'jpg')
        cmds = " "
        try:
            BLOCKS = int(args['blocks'])
            cmds += '-b {} '.format(BLOCKS)
        except:
            pass
        try:
            DITHER = bool(args['dither'])
            cmds += '-d {} '.format(DITHER)

        except:
            pass
        try:
            INTENSITY = int(args['intensity'])
            cmds += '-i {} '.format(INTENSITY)
        except:
            pass
        subprocess.call('python prismsort.py {} {}'.format(Tmp.path_, cmds))
        att = self.UploadFromDisk(Tmp.path_)
        Tmp.cachefile(Tmp.path_)
        Tmp.rem()
        R_args['attachment'] = att
        R_args['message'] = ':D'
        self.Replyqueue.put(R_args)
        return True

    def rollRows(self, args):
        R_args = {'peer_id': args['args']['peer_id'], 'v': 5.45, 'forward_messages': args['data']['message_id']}
        delta = int(args['delta']) if 'delta' in args else 20
        atts = self.UserApi.messages.getById(message_id=args['data']['message_id'])[1]['attachments']
        Topost = []
        for att in atts:
            if att['type'] == 'photo':
                try:
                    photo = att['photo']['src_xxxbig']
                except:
                    try:
                        photo = ['photo']["src_xxbig"]
                    except:
                        try:
                            photo = att['photo']["src_xbig"]
                        except:
                            try:
                                photo = att['photo']["src_big"]
                            except:
                                return False

                req = urllib.request.Request(photo, headers=self.hdr)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg')
                roll(Tmp.path_, delta)
                Tmp.cachefile(Tmp.path_)
                att = self.UploadFromDisk(Tmp.path_)
                Topost.append(att)
                Tmp.rem()
        R_args['attachment'] = Topost
        R_args['message'] = ':D'
        self.Replyqueue.put(R_args)
        return True

    def rollRowsrand(self, args):
        R_args = {}
        R_args['v'] = 5.45
        R_args['peer_id'] = args['data']['peer_id']
        atts = self.UserApi.messages.getById(message_id=args['data']['message_id'])[1]['attachments']
        Topost = []
        for att in atts:
            if att['type'] == 'photo':
                try:
                    photo = att['photo']['src_xxxbig']
                except:
                    try:
                        photo = ['photo']["src_xxbig"]
                    except:
                        try:
                            photo = att['photo']["src_xbig"]
                        except:
                            try:
                                photo = att['photo']["src_big"]
                            except:
                                return False

                req = urllib.request.Request(photo, headers=self.hdr)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg')
                rollRandom(Tmp.path_)
                att = self.UploadFromDisk(Tmp.path_)
                Topost.append(att)
                Tmp.cachefile(Tmp.path_)
                Tmp.rem()
        R_args['attachment'] = Topost
        R_args['message'] = ':D'
        self.Replyqueue.put(R_args)
        return True

    def rollRowssmart(self, args):
        R_args = {}
        R_args['v'] = 5.45
        R_args['peer_id'] = args['data']['peer_id']
        atts = self.UserApi.messages.getById(message_id=args['data']['message_id'])[1]['attachments']
        Topost = []
        for att in atts:
            if att['type'] == 'photo':
                try:
                    photo = att['photo']['src_xxxbig']
                except:
                    try:
                        photo = ['photo']["src_xxbig"]
                    except:
                        try:
                            photo = att['photo']["src_xbig"]
                        except:
                            try:
                                photo = att['photo']["src_big"]
                            except:
                                return False

                req = urllib.request.Request(photo, headers=self.hdr)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'jpg')
                rollsmast(Tmp.path_)
                Tmp.cachefile(Tmp.path_)
                att = self.UploadFromDisk(Tmp.path_)
                Topost.append(att)
                Tmp.rem()
        R_args['attachment'] = Topost
        R_args['message'] = ':D'
        self.Replyqueue.put(R_args)
        return True

    def AddImages(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        atts = data['attachments']
        #print(atts)
        if len(atts) < 2:
            args['message'] = 'Нужны 2 файла'
            self.Replyqueue.put(args)
        Topost = []

        try:

            photo = self.GetBiggesPic(atts[0], data['message_id'])
        except:
            return False
        try:
            photo1 = self.GetBiggesPic(atts[1], data['message_id'])
        except:
            return False
        req = urllib.request.Request(photo, headers=self.hdr)
        req1 = urllib.request.Request(photo1, headers=self.hdr)
        img = urlopen(req).read()
        img1 = urlopen(req1).read()
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        add(Tmp.path_, Tmp1.path_)
        att = self.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        args['attachment'] = Topost
        self.Replyqueue.put(args)

    def merge(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        atts = data['attachments']
        #print(atts)
        if len(atts) < 2:
            args['message'] = 'Нужны 2 файла'
            self.Replyqueue.put(args)
        Topost = []
        try:
            photo = self.GetBiggesPic(atts[0], data['message_id'])
        except:
            return False
        try:
            photo1 = self.GetBiggesPic(atts[1], data['message_id'])
        except:
            return False
        req = urllib.request.Request(photo, headers=self.hdr)
        req1 = urllib.request.Request(photo1, headers=self.hdr)
        img = urlopen(req).read()
        img1 = urlopen(req1).read()
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        Merge(Tmp.path_, Tmp1.path_)
        att = self.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        args['attachment'] = Topost
        self.Replyqueue.put(args)

    def KokKek(self, args, data, toCheck):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        try:
            att = data['attachments'][0]
            #print(att)
            photo = self.GetBiggesPic(att, data['message_id'])
        except:
            return False
        req = urllib.request.Request(photo, headers=self.hdr)
        img = urlopen(req).read()
        Tmp = TempFile(img, 'jpg')
        if 'кок' in toCheck:
            kok(Tmp.path_)
        if 'кек' in toCheck:
            kek(Tmp.path_)
        att = self.UploadFromDisk(Tmp.path_)
        Tmp.cachefile(Tmp.path_)
        Tmp.rem()
        args['attachment'] = att
        self.Replyqueue.put(args)

    def Filter(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        atts = self.UserApi.messages.getById(message_id=data['message_id'])[1]['attachments']
        Topost = []

        for att in atts:
            try:
                att = data['attachments'][0]
                photo = self.GetBiggesPic(att, data['message_id'])
            except:
                return False
            req = urllib.request.Request(photo, headers=self.hdr)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            m = ''
            FiltersArray = [Cartoonizer, CoolingFilter, PencilSketch, WarmingFilter, Equal,
                            AutoContrast, Neural, Tlen]

            for i in range(len(FiltersArray)):
                m += "{}.{}\n".format(i + 1, FiltersArray[i].__name__)
            args['message'] = 'Список фильтров:\n' + m
            args['forward_messages'] = data['message_id']
            self.Replyqueue.put(args)
            ans = self.WaitForMSG(5, data)
            self.LOG('log', sys._getframe().f_code.co_name, 'used filter {}'.format(ans - 1))
            print('used filter {}'.format(ans - 1))
            ImgF = FiltersArray[ans - 1]()
            ImgF.render(Tmp.path_)
            args['message'] = 'Фильтр {}'.format(FiltersArray[ans - 1].__name__)
            att = self.UploadFromDisk(Tmp.path_)

            Topost.append(att)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        args['forward_messages'] = data['message_id']
        self.Replyqueue.put(args)

    def GlitchImg(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        atts = self.UserApi.messages.getById(message_id=data['message_id'])[1]['attachments']
        Topost = []

        for att in atts:
            try:
                att = data['attachments'][0]
                photo = self.GetBiggesPic(att, data['message_id'])
            except:
                return False
            req = urllib.request.Request(photo, headers=self.hdr)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'jpg')
            Glitch2.glitch_an_image(Tmp.path_)
            att = self.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        self.Replyqueue.put(args)

    def Gif(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        a = data['message'].split(' ')
        if ('гифка' in a[1]) or ('гиф' in a[1]):
            a = ' '.join(a[2:])
        else:
            a = ' '.join(a[1:])
        args['forward_messages'] = data['message_id']
        # msg = "Вероятность того, что {}, равна {}%".format(' '.join(a), randint(0, 100))
        g = giphypop.Giphy(api_key='dc6zaTOxFJmzC')
        results = [x for x in g.search(a)]
        if results:
            gif = random.choice(results)
            page = urllib.request.Request(gif, headers=self.hdr)
            giphy = urlopen(page).read()
            soup = BeautifulSoup(giphy, 'html.parser')
            gif = soup.find_all('meta', {'itemprop': "contentUrl"})[0].get('content')

            req = urllib.request.Request(gif, headers=self.hdr)
            img = urlopen(req).read()
            Tmp = TempFile(img, 'gif')
            doc = self.UploadDocFromDisk(Tmp.path_)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
            args['attachment'] = doc
        else:

            args['message'] = "Ничего не найдено по запросу {}".format(a)
        # self.Reply(self.UserApi, args)
        self.Replyqueue.put(args)

    def Whom(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
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
            name = '{} {}'.format(user['first_name'], user['last_name'])
            replies = ["Определённо {}", "Точно {}", "Я уверен что его -  {}"]
            msg = random.choice(replies)

            while self.oldMsg == msg:
                msg = random.choice(replies)

            args['message'] = msg.format(name)
            # self.Reply(self.UserApi, args)
            self.Replyqueue.put(args)
            self.oldMsg = msg

    def Who(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        args['forward_messages'] = data['message_id']
        text = " ".join(data['message'].split(',')[1].split(' ')[2:]) if "?" not in data['message'] else " ".join(
            data['message'].split(',')[1].split(' ')[2:])[:-1]
        if "мне" in text: text = text.replace('мне', 'тебе')
        if "мной" in text: text = text.replace('мной', 'тобой')
        if "моей" in text: text = text.replace('моей', 'твоей')

        if int(data['peer_id']) <= 2000000000:
            args['message'] = "Ты"
            self.Replyqueue.put(args)
        else:
            chat = int(data['peer_id']) - 2000000000
            users = self.UserApi.messages.getChatUsers(chat_id=chat, fields='nickname', v=5.38,
                                                       name_case='nom')
            user = random.choice(users)
            if user['id'] == self.MyUId:
                args['message'] = 'Определённо Я'
                self.Replyqueue.put(args)
            name = '{} {}'.format(user['first_name'], user['last_name'])
            replies = ["Определённо {} {}", "Точно {} {}", "Я уверен что он -  {} {}"]
            msg = random.choice(replies)

            while self.oldMsg == msg:
                msg = random.choice(replies)

            args['message'] = msg.format(name, text)
            # self.Reply(self.UserApi, args)
            self.Replyqueue.put(args)
            self.oldMsg = msg

    def prob(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
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

    def Where(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        args['forward_messages'] = data['message_id']
        replies = ["Под столом", "На кровати", "За спиной", "На столе"]
        msg = random.choice(replies)
        while self.oldMsg == msg:
            msg = random.choice(replies)
        args['message'] = msg
        # self.Reply(self.UserApi, args)
        self.Replyqueue.put(args)
        self.oldMsg = msg
        # elif ',кто' in toCheck:
        #    args['peer_id'] = data['peer_id']
        #    args['v'] = 5.45
        #    args['forward_messages'] = data['message_id']
        #    if int(data['peer_id']) <= 2000000000:
        #        args['message'] = "Это точно ты"
        #        self.Replyqueue.put(args)
        #    else:
        #        chat = int(data['peer_id']) - 2000000000
        #        users = self.UserApi.messages.getChatUsers(chat_id=chat, fields='nickname', v=5.38)
        #        user = random.choice(users)
        #        if user['id'] == self.MyUId:
        #            args['message'] = 'Определённо я'
        #            self.Replyqueue.put(args)
        #            continue
        #        name = '{} {}'.format(user['first_name'], user['last_name'])
        #        replies = ["Определённо это {}", "Это точно {}", "Я уверен, что это {}", "Это {}"]
        #        msg = random.choice(replies)
        #
        #        while self.oldMsg == msg:
        #            msg = random.choice(replies)
        #
        #        args['message'] = msg.format(name)
        #        # self.Reply(self.UserApi, args)
        #        self.Replyqueue.put(args)
        #        self.oldMsg = msg

    def fullmerge(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        atts = data['attachments']
        #print(atts)
        if len(atts) < 2:
            args['message'] = 'Нужны 2 файла'
            self.Replyqueue.put(args)
        Topost = []

        try:

            photo = self.GetBiggesPic(atts[0], data['message_id'])
        except:
            return False
        try:
            photo1 = self.GetBiggesPic(atts[1], data['message_id'])
        except:
            return False
        req = urllib.request.Request(photo, headers=self.hdr)
        req1 = urllib.request.Request(photo1, headers=self.hdr)
        img = urlopen(req).read()
        img1 = urlopen(req1).read()
        Tmp = TempFile(img, 'jpg')
        Tmp1 = TempFile(img1, 'jpg')
        FullMerge(Tmp.path_, Tmp1.path_)
        att = self.UploadFromDisk(Tmp.path_)
        Topost.append(att)
        Tmp.cachefile(Tmp.path_)
        Tmp1.cachefile(Tmp1.path_)
        Tmp.rem()
        Tmp1.rem()
        args['attachment'] = Topost
        self.Replyqueue.put(args)

    def resend(self, args, data):
        args['peer_id'] = data['peer_id']
        args['v'] = 5.45
        atts = data['attachments']

        Topost = []
        for att in atts:
            try:

                photo = self.GetBiggesPic(att, data['message_id'])
            except:
                return False

            req = urllib.request.Request(photo, headers=self.hdr)

            img = urlopen(req).read()

            Tmp = TempFile(img, 'jpg')
            att = self.UploadFromDisk(Tmp.path_)
            Topost.append(att)
            Tmp.cachefile(Tmp.path_)
            Tmp.rem()
        args['attachment'] = Topost
        self.Replyqueue.put(args)
    def CheckForCommands(self):
        while True:

            sleep(1)
            data = self.Checkqueue.get()
            user = self.GetUserNameById(data['user_id'])
            self.Stat['messages'] = self.Stat['messages']+1
            try:
                self.toPrint = data['subject'] + " : " + user['first_name'] + ' ' + user['last_name'] + " : " + str(
                    data['message'])
                self.toPrint += '\n' + 'message_id : ' + str(data['message_id']) + '  peer_id : ' + str(
                    data['peer_id']) if self.DEBUG else ""
                self.LOG('message', "Command check Thread" if self.DEBUG else "Message", self.toPrint)
                print(self.toPrint)
            except:
                pass

            Commands = self.Commands
            CommandDict = {}
            args = {}
            try:
                if str(data['user_id']) in self.Settings['blacklist']:
                    self.Checkqueue.task_done()
                    continue
            except:
                pass
            if data != '':

                try:
                    if data['message'].startswith('!помощь'):
                        Command_ = data['message'].split(':')
                        args['peer_id'] = data['peer_id']
                        args['v'] = 5.45
                        args['message'] = Commands[Command_[1]][3]
                        self.Replyqueue.put(args)
                        continue
                    if '!команды' in data['message']:
                        args['peer_id'] = data['peer_id']
                        args['v'] = 5.45
                        a = ""
                        for command in Commands.keys():
                            a += 'Команда: {},{}\n'.format(command, Commands[command][2])
                        args['message'] = str(a)
                        # self.Reply(self.UserApi, args)
                        self.Replyqueue.put(args)
                        continue

                    if data['message'].startswith('!'):
                        args['peer_id'] = data['peer_id']
                        args['v'] = 5.45
                        comm = data["message"]
                        comm = comm.split("<br>")
                        User_group = 'user'
                        for C in comm[1:]:
                            C = C.split(":")
                            CommandDict[C[0].replace(" ", "").lower()] = ':'.join(C[1:])
                        Command = comm[0].replace(" ", "").lower()
                        self.LOG('command', "Command check Thread", 'Command - ', Command)
                        print('Command - ', Command)
                        CommandDict['args'] = args
                        CommandDict['data'] = data
                        try:
                            CommandDict['info'] = self.getinfo(Command) if self.getinfo(Command) != '' else "Нету инфы"
                        except:
                            continue
                        if Command in Commands:

                            for group in self.UserGroups.keys():
                                if data['user_id'] in self.UserGroups[group]:
                                    self.LOG('command', "Command check Thread", 'user check - True')
                                    print('user check - True')
                                    User_group = group

                                    print('User group - ', User_group)
                                    break
                                elif data['user_id'] not in self.UserGroups[group]:

                                    User_group = 'user'
                                    print('User group - ', User_group)
                            self.LOG('command', "Command check Thread", 'User group - ', User_group)
                            Command_Users = Commands[Command][1]
                            self.LOG('command', "Command check Thread", 'Users groups for command -', Command, ' - ',
                                     Command_Users)
                            self.LOG('command', "Command check Thread", 'access check of user - ', User_group, ' - ',
                                     User_group in Command_Users)
                            print('Users groups for command -', Command, ' - ', Command_Users)
                            print('access check of user - ', User_group, ' - ', User_group in Command_Users)
                            has_access = User_group in Command_Users
                            if has_access:
                                if not Commands[Command][4]:
                                    args['message'] = "Выполняю, подождите"
                                    self.Replyqueue.put(args)
                                self.UserApi.messages.setActivity(peer_id=data['peer_id'], type='typing', v=5.56)
                                self.Stat['commands'] = self.Stat['commands']+1

                                ret = self.ExecCommand(Commands[Command][0], CommandDict)
                            else:
                                args['forward_messages'] = data['message_id']
                                args['message'] = "Недостаточно прав"
                                self.Replyqueue.put(args)
                                self.Checkqueue.task_done()
                                continue

                            if ret == True:
                                self.Checkqueue.task_done()
                                continue
                            else:
                                args['message'] = "Не удалось выполнить"
                                self.Replyqueue.put(args)

                                # args['message'] = "Команда не распознана"
                                # self.Replyqueue.put(args)
                    if (self.MyName['first_name'].lower() in data['message'].lower()) or (
                            re.search('^((Р|р)ед)', data['message'].lower())) or (
                            re.search(r'\b(Р|р)ед\b', data['message'])):
                        toCheck = data['message'].lower().replace(' ', '')
                        self.UserApi.messages.setActivity(peer_id=data['peer_id'], type='typing', v=5.56)
                        if self.hello.search(data['message'], re.IGNORECASE):
                            args['peer_id'] = data['peer_id']
                            args['v'] = 5.45
                            replies = ["Здравствуй {}", "Хай {}", "Здравия {}", "привет {}"]
                            msg = random.choice(replies)

                            while self.oldMsg == msg:
                                msg = random.choice(replies)

                            args['message'] = msg.format(user['first_name'])
                            # self.Reply(self.UserApi, args)
                            self.Replyqueue.put(args)
                            self.oldMsg = msg
                        elif ',котики' in toCheck:
                            args['peer_id'] = data['peer_id']
                            args['v'] = 5.45
                            args['message'] = 'мимими'
                            Kotik = mimimi()
                            att = self.UploadPhoto(Kotik)
                            args['attachment'] = att
                            # self.Reply(self.UserApi, args)
                            self.Replyqueue.put(args)
                        elif ',где' in toCheck:
                            self.Where(args, data)
                        elif ',кого' in toCheck:
                            self.Whom(args, data)
                        elif ',кто' in toCheck:
                            self.Who(args, data)
                        elif (',вероятность' in toCheck) or (',инфа' in toCheck):
                            self.prob(args, data)
                        elif (',гифка' in toCheck) or (',гиф' in toCheck):
                            self.Gif(args, data)
                        elif (',кок' in toCheck) or (',кек' in toCheck):
                            self.KokKek(args, data, toCheck)
                        elif (',глюк' in toCheck):
                            self.GlitchImg(args, data)
                        elif (',обработай' in toCheck):
                            self.Filter(args, data)
                        elif (',соедини' in toCheck):
                            self.AddImages(args, data)
                        elif (',совмести' in toCheck):
                            self.merge(args, data)
                        elif (',fullmerge' in toCheck):
                            self.fullmerge(args, data)
                        elif ('savememory' in toCheck):
                            self.kernel.saveBrain("bot_brain.brn")
                        elif ('перешли' in toCheck):
                            self.resend(args, data)
                        elif "когда" in toCheck:
                            args['peer_id'] = data['peer_id']
                            args['v'] = 5.45
                            args['forward_messages'] = data['message_id']
                            args['message'] = self.generate_random_date(2)
                            self.Replyqueue.put(args)
                        elif (self.MyName['first_name'] in data['message']) or ('ред' in data['message'].lower()):
                            try:
                                msg = ' '.join(data['message'].split(' ' if ',' in data['message'] else ' ')[1:])
                                #print('bot', msg)
                                answ = self.kernel.respond(msg, sessionID=data['user_id'])
                                if answ == "IT'S HIGH NOON":
                                    att = self.UploadFromDisk(choice(['Noon1.jpg', 'Noon2.jpg']))
                                    args['attachment'] = att
                                args['peer_id'] = data['peer_id']
                                args['v'] = 5.45
                                args['message'] = self.GetUserNameById(data['user_id'])['first_name'] + ', ' + answ
                                if answ != '':
                                    self.Replyqueue.put(args)
                            except:
                                pass
                                # if data['peer_id'] == data['user_id']:
                                #     try:
                                #         answ = self.kernel.respond(data['message'], sessionID=data['user_id'])
                                #         if answ == "IT'S HIGH NOON":
                                #             att = self.UploadFromDisk(choice(['Noon1.jpg', 'Noon2.jpg']))
                                #             args['attachment'] = att
                                #         args['peer_id'] = data['peer_id']
                                #         args['v'] = 5.45
                                #         args['message'] = answ
                                #         if answ != '':
                                #             self.Replyqueue.put(args)
                                #     except:
                                #         pass



                                # if re.search(r'(В|в)сем (привет|здравия|хай)|((З|з)драсте)', data['message']):
                                #    args['peer_id'] = data['peer_id']
                                #    args['v'] = 5.45
                                #    answ = choice(['И тебе привет', 'Привет', "Здравия", "Хай"])
                                #    args['forward_messages'] = data['message_id']
                                #    args['message'] = answ
                                #    self.Replyqueue.put(args)
                except Exception as Ex:

                    args['peer_id'] = data['peer_id']
                    args['v'] = 5.45
                    self.LOG('error', "Command check Thread", Ex.__traceback__)
                    self.LOG('error', "Command check Thread", Ex.__cause__)
                    print(Ex.__traceback__)
                    print(Ex.__cause__)
                    sleep(1)
                    if 'many requests per second' in str(Ex):
                        self.LOG('error', "Command check Thread", 'Too many requests per second')
                        print('Too many requests per second')
                        # self.Checkqueue.put(data,timeout=5)
                        continue
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    TB = traceback.format_tb(exc_traceback)
                    args['message'] = "Не удалось выполнить, ошибка:{}\n {}\n {} \n {}".format(exc_type, exc_value,
                                                                                               ''.join(TB),
                                                                                               "Перешлите это сообение владельцу бота")
                    # self.Reply(self.UserApi, args)
                    self.Replyqueue.put(args)
            self.SaveConfig()
            self.Checkqueue.task_done()

    @staticmethod
    def generate_random_date(future=True, years=1):
        today = datetime.date.today()

        # Set the default dates
        day = today.day
        year = today.year
        month = today.month

        if future:
            year = random.randint(year, year + years)
            month = random.randint(month, 12)

            date_range = calendar.monthrange(year, month)[1]  # dates possible this month
            day = random.randint(day + 1, date_range)  # 1 day in the future
        else:
            year = random.randint(year, year - years)
            month = random.randint(1, month)
            day = random.randint(1, day - 1)

        return datetime.date(year, month, day)


    def GetBiggesPic(self, att, mid):
        try:
            data = self.UserApi.photos.getById(photos=att, v=5.57)[0]
        except:

            print('using MID')
            self.LOG('log', sys._getframe().f_code.co_name, 'using MID')
            data = self.UserApi.messages.getById(message_ids=mid, v=5.57)['items'][0]['attachments']
            print('mid data', data)
            #self.LOG('log',sys._getframe().f_code.co_name, 'mid data', data)
            for i in data:

                if i['type'] == 'photo' and (int(i['photo']['id']) == int(att.split('_')[1])):
                    key = i['photo']['access_key']
                    data = self.UserApi.photos.getById(photos=att, v=5.57, access_key=key)[0]

        print(data)
        sizes = re.findall(r'(?P<photo>photo_\d+)', str(data))
        print(sizes)
        sizesToSort = {int(size.split('_')[1]): size for size in sizes}

        sizesSorted = sorted(sizesToSort, reverse=True)[0]
        size = data[sizesToSort[sizesSorted]]
        print(size)
        return data[sizesToSort[sizesSorted]]

    def LongPool(self, key, server, ts):

        url = 'https://' + server + '?act=a_check&key=' + key + '&ts=' + str(ts) + '&wait=25&mode=130&version=1'
        try:

            request = requests.get(url)
            result = request.json()

        except ValueError:
            result = '{ failed: 2}'
        return result

    def GetUserFromMessage(self, message_id):
        sleep(0.25)

        try:
            uid = self.UserApi.messages.getById(message_id=message_id)[1]['uid']
            return uid
        except:
            sleep(1)
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
            self.Longpool.put(results)

    def parseLongPool(self):
        while True:
            results = self.Longpool.get()
            try:
                updates = results['updates']
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
                for update in updates:
                    s = update

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
                            atts = s[7]
                            attatchments = []
                            try:
                                rand_id = int(atts[-1])
                            except:
                                rand_id = None
                            attsFindAll = re.findall(r'attach\d+_type', str(atts))
                            for att in attsFindAll:

                                if atts[att] == 'photo':
                                    attatchments.append(atts[att.split('_')[0]])
                            args['attachments'] = attatchments

                            args['peer_id'] = from_id
                            args["message"] = text
                            args['message_id'] = message_id
                            args['date'] = timestamp
                            args['user_id'] = self.GetUserFromMessage(message_id)
                            args['atts'] = atts
                            args['subject'] = subject
                            args['v'] = 5.45
                            if text == '!':
                                continue
                            if args['user_id'] != self.MyUId and rand_id == None:
                                self.Checkqueue.put(args, timeout=60)
                                # self.CheckForCommands(args)
                                # self.Reply(self.UserApi,args)
                                # return from_id,text,subject
                        except KeyError:
                            continue
                    elif code == 8:
                        try:
                            user = self.GetUserNameById(s[1] * -1)
                            try:
                                if user['sex'] == 2:
                                    sex = 'Вошел'
                                elif user['sex'] == 1:
                                    sex = 'Вошла'
                            except:
                                sex = 'Вошло'
                            toprint = " ".join([user['first_name'], user['last_name'], ' {} в сеть'.format(sex)])
                            self.LOG('event', "VK out", toprint)
                            print(toprint)
                        except KeyError:
                            continue
                    elif code == 9:

                        try:

                            user = self.GetUserNameById(s[1] * -1)
                            try:
                                if user['sex'] == 2:
                                    sex = 'Вышел'
                                elif user['sex'] == 1:
                                    sex = 'Вышла'
                                else:
                                    sex = "Вышло"


                            except:
                                sex = 'Вышло'
                            try:
                                toprint = " ".join([user['first_name'], user['last_name'], ' {} из сети'.format(sex)])
                                self.LOG('event', "VK out", toprint)
                                print(toprint)
                            except:
                                print('Что-то пошло не так при выходе из сети')
                        except KeyError:
                            continue
                    elif code == 61:

                        try:
                            user = self.GetUserNameById(s[1])
                            toprint = " ".join([user['first_name'], user['last_name'], 'Набирает сообщение'])
                            self.LOG('event', "VK out", toprint)
                            print(toprint)
                        except:
                            continue
                    elif code == 62:
                        user = self.GetUserNameById(s[1])

                        arg = {}
                        arg['chat_id'] = s[2]

                        try:
                            chat = self.UserApi.messages.getChat(**arg)
                        except:
                            chat = {}
                            chat['title'] = 'Хз чё, но тута ошибка'

                        try:
                            toprint = " ".join(
                                [user['first_name'], user['last_name'], 'Набирает сообщение в беседе', chat['title']])
                            self.LOG('event', "VK out", toprint)
                            print(toprint)
                        except:
                            continue
                    elif code == 51:
                        try:
                            Targs = {}
                            id = str(s[1] + 2000000000)
                            if self.Settings['namelock'][id][1]:
                                chat = self.UserApi.messages.getChat(chat_id=s[1], v=5.57)['title']
                                if chat == self.Settings['namelock'][id][0]:
                                    continue
                                self.UserApi.messages.editChat(chat_id=s[1], title=self.Settings['namelock'][id][0],
                                                               v=5.57)
                                Targs['peer_id'] = id
                                Targs['v'] = 5.45
                                Targs['message'] = 'Название беседы менять запрещено'
                                self.Replyqueue.put(Targs)
                        except:
                            pass


bot = VK_Bot(debug=True)

bot.ContiniousMessageCheck()
