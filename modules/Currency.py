from Module_manager_v2 import ModuleManager

try:
    from .__Command_template import *
except:
    from __Command_template import *

from utils import ArgBuilder

@ModuleManager.command(names=['addmoney', 'addcurr'], desc='Редактирование кошелька пользователя', perm='core.currency', template='{botname}, id пользователя кол-во денег')
class Command_AddCurrency(C_template):
    name = ['addmoney', 'addcurr']
    access = ['admin']
    perm = 'core.currency'
    desc = 'Редактирование кошелька пользователя'
    template = '{botname}, id пользователя кол-во денег'


    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        text = data.text.split(' ')
        user = text[0]
        curr = text[-1]
        self.api.USERS.UpdateCurrency(user, curr)

        userName = self.api.GetUserNameById(int(user))
        try:
            args.message = 'Пользователю {} {} было добавлено {} валюты'.format(userName.first_name,
                                                                                userName.last_name,
                                                                                curr)

        except:
            args.message = 'Пользователю было добавлено {} валюты'.format(curr)
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=['setmoney', 'setcurr'], desc='Редактирование кошелька пользователя', perm='core.currency', template='{botname}, id пользователя кол-во денег')
class Command_SetCurrency(C_template):
    name = ['setmoney', 'setcurr']
    access = ['admin']
    perm = 'core.currency'
    desc = 'Редактирование кошелька пользователя'
    template = '{botname}, id пользователя кол-во денег'


    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        text = data.text.split(' ')
        user = text[0]
        curr = text[-1]
        self.api.USERS.SetCurrency(user, curr)


        userName = self.api.GetUserNameById(int(user))
        try:
            args.message = 'Пользователю {} {} было изменено кол-во валюты на {}'.format(userName.first_name,
                                                                                         userName.last_name, curr)

        except:
            args.message = 'Пользователю было изменено кол-во валюты на {}'.format(curr)
        self.api.Replyqueue.put(args)

@ModuleManager.command(names=['скинуть', 'отдолжить'], desc='Позволяет передать валюту', perm='text.giveCurr', template = '{botname}, id пользователя кол-во денег')
class Command_GiveCurr(C_template):
    name = ['скинуть', 'отдолжить']
    access = ['all']
    perm = 'text.giveCurr'
    desc = 'Позволяет передать валюту'
    template = '{botname}, id пользователя кол-во денег'

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        text = data.text.split(' ')
        user = text[0]
        curr = text[-1]
        if not self.api.USERS.isValid(user):
            args.message = 'Неизвестный пользователь. Проверьте правильность указанного вами id'
            self.api.Replyqueue.put(args)
            return
        # from
        self.api.USERS.pay(str(user), -int(curr))
        # to
        self.api.USERS.pay(str(data.user_id), int(curr))
        userName = self.api.GetUserNameById(int(user))
        try:
            args.message = 'Вы перевели {} {} {} валюты'.format(userName.first_name, userName.last_name, curr)

        except:
            args.message = 'Вы перевели пользователю {} валюты'.format(curr)
        self.api.Replyqueue.put(args)
