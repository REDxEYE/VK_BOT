from time import sleep

import sys

from Module_manager_v2 import ModuleManager

try:
    from .__Command_template import *
except ImportError:
    from __Command_template import *

from ExtLib.Raspberry_PI import *
from utils import ArgBuilder
@ModuleManager.command(names= ['pistat', 'PI', 'малина'], desc='Выводит информацию о RaspberryPi', perm='core.PI', template='{botname}, малина')
class Command_PiStat(C_template):
    name = ['pistat', 'PI', 'малина']
    access = ['admin']
    perm = 'core.PI'
    desc = 'Выводит информацию о RaspberryPi'
    enabled = True
    
    
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        template = 'Темпуратура CPU {} градусов\n' \
                   'Загруженность CPU {}%\n' \
                   'Оперативная память {}Мб\n' \
                   'Места на диске {}\n'
        msg = template.format(getCPUtemperature(), getCPUuse(), round(int(getRAMinfo()[2])/1024,3), getDiskSpace()[2])
        data.send_back(msg)


class Command_GITPULL(C_template):
    name = ['update', 'git']
    access = ['admin']
    perm = 'core.update'
    desc = 'git pull and git chechout'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        text = []
        p = os.popen('git pull -f')

        text.append(p.readline())
        t = 0
        while p != '':
            text.append(p.readline())
            t += 1
            if t > 100:
                break
        data.send_back('\n'.join(text))

class Command_LevelUP(C_template):
    name = ['levelup']
    access = ['admin']
    perm = 'core.LEVELUP'
    desc = 'FULL UPDATE AND RESTART'
    template = '{botname}, THERE NO FUCKING HELP FOR YOU'

    @staticmethod
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        msg = 'Запущена процедура обновления!'
        data.send_back(msg, [], True)
        p = os.popen('git pull -f')
        text = []
        text.append(p.readline())
        t = 0
        while p != '':
            text.append(p.readline())
            t += 1
            if t > 100:
                break

        data.send_back('\n'.join(text))
        sleep(1)
        data.send_back('Загрузка обновления закончена')
        sleep(1)
        data.send_back('Перезагрузка!')
        sleep(3)
        os.execl(sys.executable,sys.executable, os.path.join(self.api.ROOT, 'Vk_bot2.py'))