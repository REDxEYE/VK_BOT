from Module_manager_v2 import ModuleManager

try:
    from .__Command_template import *
except:
    from __Command_template import *

from utils import ArgBuilder

@ModuleManager.command(names=['addmoney', 'addcurr'], desc='Редактирование кошелька пользователя', perm='core.currency', template='{botname}, id пользователя кол-во денег')
class Command_AddCurrency(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        text = data.text.split(' ')
        user = text[0]
        curr = text[-1]
        self.api.USERS.UpdateCurrency(user, curr)

        userName = self.api.GetUserNameById(int(user))
        try:
            msg = 'Пользователю {} {} было добавлено {} валюты'.format(userName.first_name,
                                                                                userName.last_name,
                                                                                curr)

        except:
            msg = 'Пользователю было добавлено {} валюты'.format(curr)
        data.send_back(msg, [], True)

@ModuleManager.command(names=['setmoney', 'setcurr'], desc='Редактирование кошелька пользователя', perm='core.currency', template='{botname}, id пользователя кол-во денег')
class Command_SetCurrency(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        text = data.text.split(' ')
        user = text[0]
        curr = text[-1]
        self.api.USERS.SetCurrency(user, curr)


        userName = self.api.GetUserNameById(int(user))
        try:
            msg = 'Пользователю {} {} было изменено кол-во валюты на {}'.format(userName.first_name,
                                                                                         userName.last_name, curr)

        except:
            msg = 'Пользователю было изменено кол-во валюты на {}'.format(curr)
        data.send_back(msg, [], True)

@ModuleManager.command(names=['скинуть', 'отдолжить'], desc='Позволяет передать валюту', perm='text.giveCurr', template = '{botname}, id пользователя кол-во денег')
class Command_GiveCurr(C_template):
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        text = data.text.split(' ')
        user = text[0]
        curr = text[-1]
        if not self.api.USERS.isValid(user):
            msg = 'Неизвестный пользователь. Проверьте правильность указанного вами id'
            data.send_back(msg, [], True)
            return
        # from
        self.api.USERS.pay(str(user), -int(curr))
        # to
        self.api.USERS.pay(str(data.user_id), int(curr))
        userName = self.api.GetUserNameById(int(user))
        try:
            msg = 'Вы перевели {} {} {} валюты'.format(userName.first_name, userName.last_name, curr)

        except:
            msg = 'Вы перевели пользователю {} валюты'.format(curr)
        data.send_back(msg, [], True)
