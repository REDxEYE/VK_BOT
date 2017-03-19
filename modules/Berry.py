try:
    from .__Command_template import *
except:
    from __Command_template import *
from ExtLib.Raspberry_PI import *


class Command_PiStat(Command_template):
    name = ['pistat', 'PI', 'малина']
    access = ['admin']
    perm = 'core.PI'
    desc = 'Выводит информацию о RaspberryPi'

    @staticmethod
    def execute(bot, data, forward=True):
        args = {"peer_id": data['peer_id'], "v": "5.60", }
        if forward:
            args.update({"forward_messages": data['message_id']})
        template = 'Темпуратура CPU {}\n' \
                   'Загруженность CPU {}' \
                   'Оперативная память {}\n' \
                   'Места на диске {}\n'
        msg = template.format(getCPUtemperature(), getCPUuse(), getRAMinfo()[2], getDiskSpace()[1])
        args['message'] = msg
        bot.Replyqueue.put(args)
