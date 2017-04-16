import json
import os, os.path
import threading
import urllib
from time import sleep
from urllib.request import urlopen

import requests

from DataTypes.attachments import attachment
from Module_manager_v2 import ModuleManager
from libs.tempfile_ import TempFile
from trigger import Trigger
from utils.StringBuilder import StringBuilder

try:
    import execjs

    execjsAvalible = True
except:
    execjsAvalible = False
    execjs = None

import Vk_bot2
from DataTypes.LongPoolHistoryUpdate import LongPoolHistoryMessage, Updates
from DataTypes.group import group, contacts_group
from DataTypes.doc import doc
import DataTypes
from modules.__Command_template import C_template
from utils import ArgBuilder
from libs import VK_foaf

HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


@ModuleManager.command(names=['группа', 'groupinfo'], perm='text.groupinfo', desc="Выводит инфу о группе",
                       template='{botname}, группа ID группы')
class Command_GetGroup(C_template):
    name = ['группа', 'groupinfo']
    access = ['user']
    perm = 'text.groupinfo'
    template = '{botname}, группа '

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        if len(data.args) < 1:
            return False
        g = group.Fill(self.api.UserApi.groups.getById(v='5.60', group_id=data.args[0],
                                                       fields=['city', 'country', 'place', 'description', 'wiki_page',
                                                               'members_count', 'counters', 'start_date', 'finish_date',
                                                               'can_post', 'can_see_all_posts', 'activity', 'status',
                                                               'contacts', 'links', 'fixed_post', 'verified', 'site',
                                                               'ban_info', 'cover'])[0])  # type: group
        ContactTemplate = "{} {} - {}. {}"
        GroupTemplate = 'Группа {}\n' \
                        'Кол-во участников {}\n' \
                        'Описание : {}\n' \
                        'Контактные данные:\n'
        contacts = []  # type: list[str]
        print(g.contacts)
        for contact in g.contacts:  # type: contacts_group
            print(contact)
            user = self.api.GetUserNameById(contact.user_id)

            contacts.append(ContactTemplate.format(user.first_name, user.last_name, contact.desc,
                                                   contact.phone if contact.phone != None else ""))
            sleep(0.2)
        args.message = GroupTemplate.format(g.name, g.members_count, g.description) + '\n'.join(contacts)

        self.api.Replyqueue.put(args.AsDict_())


@ModuleManager.command(names=['whois'], perm='text.whois',
                       desc="Выводит информацию о статусе и правах пользователя у бота", template='{botnmae}, whois')
class Command_Whois(C_template):
    name = ['whois']
    access = ['user']
    desc = 'Выводит информацию о вашем статусе и правах у бота'
    perm = 'text.whois'
    template = '{botnmae}, whois'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        bb = data.text.split(' ')

        try:
            userperms = self.api.USERS.GetPerms(bb[0])
            userstatus = self.api.USERS.GetStatus(bb[0])
        except:
            userperms = "Не зарегестрирован"
            userstatus = "Не зарегестрирован"

        try:
            UD = VK_foaf.GetUser(bb[0])
        except:
            UD = {}
            UD['reg'] = "ОШИБКА"
            UD['Bday'] = "ОШИБКА"
            UD['gender'] = "ОШИБКА"
        userName = self.api.GetUserNameById(int(bb[0]))

        msg_template = "Cтатус пользователя - {}\nЕго ФИО - {} {}\nЕго права :\n{}\nЗарегистрирован {}\nДень рождения {}\n пол {}\n"
        msg = msg_template.format(userstatus, userName.first_name, userName.last_name,
                                  ',\n'.join(userperms) if isinstance(userperms, list) else userperms, UD['reg'],
                                  UD['Bday'], UD['gender'])
        args['message'] = msg
        self.api.Replyqueue.put(args)


@ModuleManager.command(names=['whoami', "uname",'профиль'], perm='text.whoami',
                       desc="Выводит информацию о вашем статусе и правах у бота", template='{botnmae}, whoami')
class Command_AboutUser(C_template):
    name = ['whoami', "uname"]
    access = ['user']
    desc = 'Выводит информацию о вашем статусе и правах у бота'
    perm = 'text.whoami'
    template = '{botname}, whoami'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)

        userperms = self.api.USERS.GetPerms(data.user_id)
        userstatus = self.api.USERS.GetStatus(data.user_id)
        UD = VK_foaf.GetUser(data.user_id)
        string = StringBuilder(sep='────────────')
        string +=f"Ваш статус - {userstatus}\n"
        msg = f"Ваш id - {data.user_id}\n" \
             f"Ваши права :\n" \
             f"{os.linesep.join(userperms)}\n" \
             f"Зарегистрирован {UD['reg']}\n" \
             f"День рождения {UD['Bday']}\n" \
             f"пол {UD['gender']}\n" \
             f"Кол-во внутренней валюты: {self.api.USERS.GetCurrency(data.user_id)}\n"
        args['message'] = msg
        self.api.Replyqueue.put(args)


@ModuleManager.command(names=['evaljs'], perm='core.EvJs', desc='Выполняет JS скрипт')
class Command_EvalJS(C_template):
    enabled = execjsAvalible
    name = ['evaljs']
    access = ['admin']
    desc = 'Выполняет JS скрипт'
    perm = 'core.EvJs'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        code = self.api.html_decode(' '.join(data.body.split('<br>')[1:]))
        JavaScript = execjs.get(execjs.runtime_names.Node)
        print('JavaScript runtime -- ', execjs.get().name)
        js = JavaScript.eval(code)

        args['message'] = 'Выполнено {}\n{}'.format(execjs.get().name, js)
        self.api.Replyqueue.put(args)


@ModuleManager.command(names=['execjs'], perm='core.ExJs', desc='Выполняет JS скрипт, (вызываетмый метод - exec)')
class Command_ExecJS(C_template):
    enabled = execjsAvalible
    name = ['execjs']
    access = ['admin']
    desc = 'Выполняет JS скрипт, (вызываетмый метод - exec)'
    perm = 'core.ExJs'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        code = self.api.html_decode(' '.join(data.body.split('<br>')[1:]))
        JavaScript = execjs.get(execjs.runtime_names.Node)
        print('JavaScript runtime -- ', execjs.get().name)
        js = JavaScript.compile(code)
        js = js.call('exec')

        args['message'] = 'Выполнено {}\n{}'.format(execjs.get().name, js)
        self.api.Replyqueue.put(args)


@ModuleManager.command(names=['shutdown'], perm='core.shutdown', desc='Выключение бота', template='{botname}, shutdown')
class Command_quit(C_template):
    name = ["shutdown"]
    access = ["admin"]
    desc = "Выключение бота"
    perm = 'core.shutdown'
    template = '{botname}, shutdown'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id,
                "message": "Увидимся позже"}
        self.api.Replyqueue.put(args)
        sleep(2)
        os._exit(0)


@ModuleManager.command(names=['рестарт'], perm='core.restart', desc='Рестарт бота', template='{botname}, рестарт')
class Command_restart(C_template):
    name = ["рестарт"]
    access = ['admin']
    desc = "Рестарт бота"
    perm = 'core.restart'
    template = '{botname}, рестарт'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        import sys
        os.execl(sys.executable, sys.executable, os.path.join(self.api.ROOT, 'Vk_bot2.py'))


@ModuleManager.command(names=["py", "python"], perm='core.PY', desc="Выполняет код из сообщения",
                       template='{botname}, py\nВаш код здесь')
class Command_ExecCode(C_template):
    name = ["py", "python"]
    access = ['admin']
    desc = "Выполняет код из сообщения"
    perm = 'core.PY'
    template = '{botname}, py\nВаш код здесь'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        code = self.api.html_decode(data.body)

        code = '\n'.join(code.split('\n')[1:]).replace('|', '  ')
        code = code.replace('print', 'print_')
        a = compile(code, '<string>', 'exec')
        from io import StringIO
        import contextlib, sys, traceback

        @contextlib.contextmanager
        def stdoutIO(stdout=None):
            old = sys.stdout
            if stdout is None:
                stdout = StringIO()
            sys.stdout = stdout
            yield stdout
            sys.stdout = old

        l = {'api': self.api.UserApi, 'bot': self.api}
        g = {'os': None}
        with stdoutIO() as s:
            try:
                exec(a, g, l)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                TB = traceback.format_tb(exc_traceback)

                args['message'] = "Не удалось выполнить, ошибка:{}\n {}\n {} \n {}".format(exc_type, exc_value,
                                                                                           ''.join(TB),
                                                                                           "Перешлите это сообщение владельцу бота")
                self.api.Replyqueue.put(args)
                return
        template = """Принты:\n{}\nФинальный ответ:\n{}\n """
        out = template.format(s.getvalue(), str(l['out']) if 'out' in l else "None")
        args['message'] = out
        self.api.Replyqueue.put(args)
        return True


import inspect


@ModuleManager.command(names=["triggers"], perm='core.triggers', desc='Выводит список тригеров')
class Command_triggers(C_template):
    name = ['triggers']
    access = ['admin']
    desc = 'Выводит список тригеров'
    perm = 'core.triggers'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        triggers = self.api.TRIGGERS
        t = []  # type: list[str]
        trigger_template = 'Тригер №{}\n' \
                           'Условие : {}\n' \
                           'Таймаут : {}\n' \
                           'Одноразовый : {}\n' \
                           'Бесконечный : {}\n'
        if triggers.HasActive:
            for n, trigger in enumerate(triggers.triggers):  # type: (int,Trigger)
                lamb = inspect.getsource(trigger.cond)
                lamb = lamb[lamb.find('lambda'):lamb.find(',', lamb.find('lambda'))]
                t.append(trigger_template.format(n, lamb, trigger.timeout, trigger.onetime, trigger.infinite))
            args.message = '\n'.join(t) + '\n.'
        else:
            args.message = 'Нету активных тригеров'

        self.api.Replyqueue.put(args.AsDict_())


@ModuleManager.command(names=['setprefix', 'префикс'], perm='core.prefix', desc='Устанавливает префикс')
class Command_SetPrefix(C_template):
    name = ['setprefix', 'префикс']
    access = ['admin']
    desc = 'Устанавливает префикс'
    perm = 'core.prefix'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        if len(data.args) == 1:
            self.api.prefix = data.args[0]
            self.api.SaveConfig()
            args.message = 'Новый префикс "{}" установлен'.format(data.args[0])
        else:
            args.message = 'Текущий префикс - {}'.format(self.api.prefix)
        self.api.Replyqueue.put(args.AsDict_())


@ModuleManager.command(names=['чат', 'chat'], perm='core.currchat', desc='Выводит инфу о чата')
class Command_CurChat(C_template):
    name = ['чат', 'chat']
    access = ['admin']
    desc = 'Выводит инфу о чата'
    perm = 'core.currchat'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        if data.isChat:
            '''
            Информация о беседе 22:
            • Название: /dev/5nights
            • Создатель: 357638927
            • Фотография: TODO
            • Пользователи: [357638927, 163130349, 208128019, 199517787, 384380531]'''
            template = '»Номер беседы {}\n' \
                       '»Название беседы {}\n' \
                       '»Админ {}\n' \
                       '»Список пользователей {}\n'
            chat = Updates.GetChat(int(data.chat_id) - 2000000000)
            print(chat.photo_200)
            args.attachment = self.api.UploadPhoto(chat.photo_200)
            args.message = template.format(str(chat.id), chat.title, str(chat.admin_id),
                                           ('\n{}'.format('&#127;' * 23)).join(map(str, chat.users)))
        else:
            args.message = 'Ну... Это как бы личка...'
        self.api.Replyqueue.put(args.AsDict_())


import DataTypes.doc
from PIL import Image
from io import BytesIO


@ModuleManager.command(names=['граффити'], perm='core.graphity', desc='Заливает как графити')
class Command_Graphity(C_template):
    name = ['граффити']
    access = ['admin']
    desc = 'Заливает как графити'
    perm = 'core.graphity'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id

        apiurl = 'https://api.vk.com/method/docs.getUploadServer?access_token={}&type=graffiti&v=5.60'.format(
            self.api.UserAccess_token)
        server = json.loads(urlopen(apiurl).read().decode('utf-8'))['response']['upload_url']
        att = data.attachments[0]  # type: attachment

        if att.type == attachment.types.doc:
            if att.doc.type == DataTypes.doc.doc.DocTypes.gif or att.doc.type == DataTypes.doc.doc.DocTypes.img:
                gif = att.doc.url
                req = urllib.request.Request(gif, headers=HDR)
                img = urlopen(req).read()
                Tmp = TempFile(img, 'png')
                req = requests.post(server, files={'file': open(Tmp.path_, 'rb')})
                Tmp.rem()
                if req.status_code == requests.codes.ok:
                    print(req.text)
                    params = {'file': req.json()['file'], 'v': '5.60'}
                    doc = self.api.UserApi.docs.save(**params)[0]
                    Graff = 'doc{}_{}'.format(doc['owner_id'], doc['id'])
                    args.attachment = Graff

            elif att.doc.type == DataTypes.doc.doc.DocTypes.audio:
                args.message = 'Аудио нельзя'
            elif att.doc.type == DataTypes.doc.doc.DocTypes.archive:
                args.message = 'Архивы нельзя'
            elif att.doc.type == DataTypes.doc.doc.DocTypes.Ebook:
                args.message = 'Книги нельзя'
            elif att.doc.type == DataTypes.doc.doc.DocTypes.video:
                args.message = 'Видео нельзя'
            else:
                args.message = 'Это нельзя'
        if att.type == attachment.types.photo:
            photo_url = att.photo.GetHiRes
            req = urllib.request.Request(photo_url, headers=HDR)
            img = Image.open(BytesIO(urlopen(req).read()))
            Tmp = TempFile.generatePath('png')
            img.save(Tmp)
            req = requests.post(server, files={'file': open(Tmp, 'rb')})
            os.remove(Tmp)
            if req.status_code == requests.codes.ok:
                print(req.text)
                params = {'file': req.json()['file'], 'v': '5.60'}
                doc = self.api.UserApi.docs.save(**params)[0]
                Graff = 'doc{}_{}'.format(doc['owner_id'], doc['id'])
                args.attachment = Graff
        self.api.Replyqueue.put(args)


@ModuleManager.command(names=['threads', "потоки"], perm='core.threads', desc='List all threads')
class Command_Threads(C_template):
    name = ['threads', "потоки"]
    access = ['admin']
    desc = 'List all threads'
    perm = 'core.threads'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        threads = []
        template = 'Поток {}: жив - {}'

        for th in threading.enumerate():  # type: threading.Thread
            threads.append(template.format(th.name, th.isAlive()))
        args.message = '\n'.join(threads) + '\nВсего живых - {}'.format(threading.active_count())
        self.api.Replyqueue.put(args)


@ModuleManager.command(names=['обновименя'], perm='text.updateCache', desc='Обновляек кэш пользователя')
class Command_updateCache(C_template):
    name = ['обновименя']
    access = ['all']
    desc = 'Обновляек кэш пользователя'
    perm = 'text.updateCache'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        self.api.GetUserNameById(int(data.user_id), update=True)

@ModuleManager.command(names=['очисти'],perm = 'core.clearDDB',desc='Удаляет пользователя их базы пользователей',template='{botname}, очисти ud1 ud2 .... ud999')
class ClearBD(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates,):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)

        for target in data.args:
            try:
                user = DataTypes.user.user.Fill(self.api.USERS.DB[target]['cache'])
                del self.api.USERS.DB[target]
                args.message += f'Пользователь {user.Name} был удалён из базы данных\n'


            except KeyError:
                continue
        self.api.Replyqueue.put(args)
