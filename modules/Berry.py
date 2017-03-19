from time import sleep

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
        template = 'Темпуратура CPU {}\n' \
                   'Загруженность CPU {}\n' \
                   'Оперативная память {}\n' \
                   'Места на диске {}\n'
        msg = template.format(getCPUtemperature(), getCPUuse(), getRAMinfo()[2], getDiskSpace()[1])
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

