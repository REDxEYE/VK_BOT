try:
    from .__Command_template import *
except:
    from __Command_template import *

from utils import ArgBuilder


class Command_AddCurrency(C_template):
    name = ['addmoney', 'addcurr']
    access = ['admin']
    perm = 'core.currency'
    desc = 'Редактирование кошелька пользователя'
    template = '{botname}, id пользователя кол-во денег'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, forward=True):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        text = data.text.split(' ')
        user = text[0]
        curr = text[-1]
        bot.USERS.UpdateCurrency(user, curr)

        userName = bot.GetUserNameById(int(user))
        try:
            args.message = 'Пользователю {} {} было добавлено {} валюты'.format(userName.first_name,
                                                                                userName.last_name,
                                                                                curr)

        except:
            args.message = 'Пользователю было добавлено {} валюты'.format(curr)
        bot.Replyqueue.put(args)


class Command_SetCurrency(C_template):
    name = ['setmoney', 'setcurr']
    access = ['admin']
    perm = 'core.currency'
    desc = 'Редактирование кошелька пользователя'
    template = '{botname}, id пользователя кол-во денег'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, forward=True):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        text = data.text.split(' ')
        user = text[0]
        curr = text[-1]
        bot.USERS.SetCurrency(user, curr)


        userName = bot.GetUserNameById(int(user))
        try:
            args.message = 'Пользователю {} {} было изменено кол-во валюты на {}'.format(userName.first_name,
                                                                                         userName.last_name, curr)

        except:
            args.message = 'Пользователю было изменено кол-во валюты на {}'.format(curr)
        bot.Replyqueue.put(args)


class Command_GiveCurr(C_template):
    name = ['скинуть', 'отдолжить']
    access = ['all']
    perm = 'text.giveCurr'
    desc = 'Позволяет передать валюту'
    template = '{botname}, id пользователя кол-во денег'

    @staticmethod
    def execute(bot: Vk_bot2.Bot, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, forward=True):
        args = ArgBuilder.Args_message()
        args.peer_id = data.chat_id
        args.forward_messages = data.id
        text = data.text.split(' ')
        user = text[0]
        curr = text[-1]
        if not bot.USERS.isValid(user):
            args.message = 'Неизвестный пользователь. Проверьте правильность указанного вами id'
            bot.Replyqueue.put(args)
            return
        # from
        bot.USERS.pay(str(user), -int(curr))
        # to
        bot.USERS.pay(str(data.user_id), int(curr))
        userName = bot.GetUserNameById(int(user))
        try:
            args.message = 'Вы перевели {} {} {} валюты'.format(userName.first_name, userName.last_name, curr)

        except:
            args.message = 'Вы перевели пользователю {} валюты'.format(curr)
        bot.Replyqueue.put(args)
