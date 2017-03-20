from time import sleep

import sys

try:
    from .__Command_template import *
except:
    from __Command_template import *

from ExtLib.Raspberry_PI import *


class Command_PiStat(C_template):
    name = ['pistat', 'PI', 'малина']
    access = ['admin']
    perm = 'core.PI'
    desc = 'Выводит информацию о RaspberryPi'
    enabled = True
    @staticmethod
    def execute(bot, data, forward=True):
        args = {"peer_id": data['peer_id'], "v": "5.60", }
        if forward:
            args.update({"forward_messages": data['message_id']})
        template = 'Темпуратура CPU {} градусов\n' \
                   'Загруженность CPU {}%\n' \
                   'Оперативная память {}Мб\n' \
                   'Места на диске {}\n'
        msg = template.format(getCPUtemperature(), getCPUuse(), round(int(getRAMinfo()[2])/1024,3), getDiskSpace()[2])
        args['message'] = msg
        bot.Replyqueue.put(args)


class Command_GITPULL(C_template):
    name = ['update', 'git']
    access = ['admin']
    perm = 'core.update'
    desc = 'git pull and git chechout'

    @staticmethod
    def execute(bot, data, forward=True):
        args = {"peer_id": data['peer_id'], "v": "5.60", }
        if forward:
            args.update({"forward_messages": data['message_id']})
        text = []
        p = os.popen('git pull -f')

        text.append(p.readline())
        t = 0
        while p != '':
            text.append(p.readline())
            t += 1
            if t > 100:
                break
        args['message'] = '\n'.join(text)
        bot.Replyqueue.put(args)

class Command_LevelUP(C_template):
    name = ['levelup']
    access = ['admin']
    perm = 'core.LEVELUP'
    desc = 'FULL UPDATE AND RESTART'
    template = 'THERE NO FUCKING HELP FOR YOU'

    @staticmethod
    def execute(bot, data, forward=True):
        args = {"peer_id": data['peer_id'], "v": "5.60", }
        if forward:
            args.update({"forward_messages": data['message_id']})
        args['message'] = 'Запущена процедура обновления!'
        bot.Replyqueue.put(args)
        p = os.popen('git pull -f')
        text = []
        text.append(p.readline())
        t = 0
        while p != '':
            text.append(p.readline())
            t += 1
            if t > 100:
                break
        args['message'] = '\n'.join(text)
        bot.Replyqueue.put(args)
        sleep(0.5)
        args['message'] = 'Загрузка обновления закончена'
        bot.Replyqueue.put(args)
        args['message'] = 'Перезагрузка!'
        sleep(0.5)
        bot.Replyqueue.put(args)
        os.execl(sys.executable,sys.executable, os.path.join(bot.ROOT, 'Vk_bot2.py'))