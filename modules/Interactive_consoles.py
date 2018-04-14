import contextlib
import time
import traceback
from io import StringIO
import sys

import ConsoleLogger
from Module_manager_v2 import ModuleManager
import trigger

try:
    from .__Command_template import *
except ImportError:
    from __Command_template import *
LOGGER = ConsoleLogger.ConsoleLogger('VK')
# @ModuleManager.command(names=["ilua"], perm='core.ilua', desc="Запускает сессию луа терминала", cost=2)
# class Command_iLua(C_template):
#
#     def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates ):
#         args = ArgBuilder.Args_message()
#         args.peer_id = data.chat_id
#         args.forward_messages = data.id
#         self.trig = trigger.Trigger(cond=lambda Tdata:Tdata.user_id==data.user_id and Tdata.chat_id == data.chat_id,
#                                callback=self.processLua,timeout = 20,onetime = False)
#         self.api.TRIGGERS.addTrigger(self.trig)
#         self.api.USERS.DB[str(data.user_id)]['iluaSession'] = True
#         luag = lua.globals()
#         luag['API'] = self.api
#         luag['print'] = print
#         msg = 'Запущена интерактивная сессия LUA консоли'
#         data.send_back(msg, [], True)
#
#     def processLua(self, data: LongPoolHistoryMessage, result):
#         @contextlib.contextmanager
#         def stdoutIO(stdout=None):
#             old = sys.stdout
#             if stdout is None:
#                 stdout = StringIO()
#             sys.stdout = stdout
#             yield stdout
#             sys.stdout = old
#         args = ArgBuilder.Args_message()
#         args.peer_id = data.chat_id
#         args.forward_messages = data.id
#         if data.body.startswith('exit'):
#             self.api.USERS.DB[str(data.user_id)]['iluaSession'] = False
#             msg = 'Завершена интерактивная сессия LUA консоли'
#             data.send_back(msg, [], True)
#             self.api.TRIGGERS.triggers.remove(self.trig)
#             return True
#         if result:
#             self.trig.timestart = time.time()
#
#             with stdoutIO() as s:
#                 ret = lua.execute(data.body)
#             print(s.getvalue())
#             msg = ret if s.getvalue()=='' else s.getvalue()
#             data.send_back(msg, [], True)
#         else:
#             self.api.USERS.DB[str(data.user_id)]['iluaSession'] = False
#             msg = 'Таймаут сессии интерактивной LUA консоли'
#             data.send_back(msg, [], True)
@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old
@ModuleManager.command(names=["ipython",'ipy'], perm='core.ipy', desc="Запускает сессию python терминала", cost=2)
class Command_iPy(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates ):
        self.trig = trigger.Trigger(cond=lambda Tdata:Tdata.user_id==data.user_id and Tdata.chat_id == data.chat_id,
                               callback=self.processPy,timeout = 50,onetime = False)
        self.api.TRIGGERS.addTrigger(self.trig)
        self.api.USERS.DB[str(data.user_id)]['ipySession'] = True
        if not self.api.USERS.DB[str(data.user_id)].get('ipyState',None):
            self.api.USERS.DB[str(data.user_id)]['ipyState'] = {}
        msg = 'Запущена интерактивная сессия Python консоли'
        data.send_back(msg, [], True)

    def processPy(self, data: LongPoolHistoryMessage, result):

        if data.body.startswith('exit'):
            self.api.USERS.DB[str(data.user_id)]['ipySession'] = False
            msg = 'Завершена интерактивная сессия Python консоли'
            data.send_back(msg, [], True)
            self.api.TRIGGERS.triggers.remove(self.trig)
            return True
        if result:
            self.trig.timestart = time.time()
            code = data.body
            a = compile(code, "iPy", 'exec')
            stdout = StringIO(newline="")
            _print = lambda *args, **kwargs: print(*args, **kwargs, file=stdout)

            g = {'print': _print,'api': self.api.UserApi, 'bot': self.api}
            l = self.api.USERS.DB[str(data.user_id)]['ipyState']
            try:
                exec(a, g, l)
                self.api.USERS.DB[str(data.user_id)]['ipyState'] = l
                msg = stdout.getvalue()
                data.send_back(msg, [], True)
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                TB = traceback.format_tb(exc_traceback)
                print(TB, exc_type, exc_value)
                msg = str(TB)+'\n'+f"{exc_type}: {exc_value}"
                data.send_back(msg, [], True)


        else:
            self.api.USERS.DB[str(data.user_id)]['ipySession'] = False
            msg = 'Таймаут сессии интерактивной Python консоли'
            data.send_back(msg, [], True)