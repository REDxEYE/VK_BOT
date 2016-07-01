import os
from math import ceil
from time import sleep
import vk
import os
import json
from datetime import datetime, timedelta

V = 1.5

def getpath():
    return os.path.dirname(os.path.abspath(__file__))


class FifeNights():
    def __init__(self):
        self.LoadConfig()
        self.Group = "-75615891"
        self.GroupDomain = "5nights"
        self.GroupAccess_token = "f27b32a27bd2ce47bde629d4323fc50ee5cc8e3a55b4955973344c56fc903a19c6825ea70e6e278aef3b5"
        self.UserAccess_token = 'c4b2c76c4089453fac5da6015eb6f5c732e3e1486be288430fcb356f1d4a97a52f535f5ec646e8052c4fb'
        self.UserSession = vk.Session(access_token=self.UserAccess_token)
        self.GroupSession = vk.Session(access_token=self.GroupAccess_token)
        self.UserApi = vk.API(self.UserSession)
        self.GroupApi = vk.API(self.GroupSession)

    def ClearPosts(self, Posts=None, treshholdTime=10, treshholdLikes=10):
        if Posts == None:
            Posts = self.posts
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
        sleep(0.3)
        User = self.UserApi.users.get(user_ids=Id)[0]
        return User['first_name'] + " " + User['last_name']

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
        with open(path + '/config.json', 'r') as config:
            self.data = json.load(config)

    def SaveConfig(self):
        path = getpath()
        with open(path + '/config.json', 'w') as config:
            json.dump(self.data, config)

    def AddUser(self, args):
        print(args)
        if "группа" in args:
            Group = args['группа']
        else:
            Group = "user"
        if 'id' in args:
            if Group in self.data:
                Ids = self.data[Group]
                Ids.append(args['id'])
                self.data[Group] = Ids
            else:
                self.data[Group] = [int(args['id'])]

            self.SaveConfig()
            return True
        else:
            return False

    def ExecCommand(self, command, args):
        return command(args)

    def Reply(self, args):
        pass
        self.GroupApi.messages.send(**args)

    def CheckForCommands(self, StartCommand="!Команда", count=10):
        CommandDict = {}

        Dialogs = self.GroupApi.messages.getDialogs(count=count)

        Commands = {
            'пост': [self.MakePost, ['admin', 'editor', 'moderator']],
            'бан': [self.BanUser, ['admin', 'editor', 'moderator']],
            'добавить': [self.AddUser, ['admin']],
        }
        for Dialog in Dialogs[1:]:
            # print(Dialog)

            if StartCommand in Dialog['body']:
                args = {}
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
                    for group in self.data:
                        if int(user_id) in self.data[group]:
                            User_group = group
                    if User_group in Commands[CommandDict["!команда"].replace(" ", "")][1] or 'all' in \
                            Commands[CommandDict["!команда"].replace(" ", "")][1]:
                        ret = self.ExecCommand(Commands[CommandDict["!команда"].replace(" ", "")][0], CommandDict)
                    else:
                        ret = False
                        args['message'] = "!Недостаточно прав"
                        self.Reply(args)
                        # self.GroupApi.messages.send(user_id=user_id, peer_id=self.Group, message="!Недостаточно прав",v="5.38")
                    if ret == True:
                        args['message'] = "!Выполннено"
                        self.Reply(args)
                        # self.GroupApi.messages.send(user_id=user_id, peer_id=self.Group, message="!Выполннено",v="5.38")
                    else:
                        args['message'] = "!Не удалось выполнить"
                        self.Reply(args)
                        # self.GroupApi.messages.send(user_id=Dialog["uid"], peer_id=self.Group, message="!Не удалось выполнить",v="5.38")
                else:
                    args['message'] = "!Команда не распознана"
                    self.Reply(args)
                    # self.GroupApi.messages.send(user_id=Dialog["uid"], peer_id=self.Group,message="Команда не распознана", v="5.38")

    def getMus(self):
        music = self.UserApi.audio.get(count=6000)
        print(music)


A = FifeNights()
# print(A.CheckWall("5nights"))
# A.ClearPosts()
A.CheckForCommands()
# print(A.getMus())
# print(A.GetChats())
