try:
    from .__Command_template import *
except:
    from __Command_template import *


class Command_AddCurrency(Command_template):
    name = ['addmoney', 'addcurr']
    access = ['admin']
    perm = 'core.currency'
    desc = 'Редактирование кошелька пользователя'

    @staticmethod
    def execute(bot, data, forward=True):
        text = data['text'].split(' ')
        user = text[0]
        curr = text[-1]
        bot.USERS.UpdateCuttency(user, curr)
        args = {"peer_id": data['peer_id'], "v": "5.60", }
        if forward:
            args.update({"forward_messages": data['message_id']})

        userName = bot.GetUserNameById(user)
        try:
            args['message'] = 'Пользователю {} {} было добавлено {} валюты'.format(userName['first_name'],
                                                                                   userName['last_name'],
                                                                                   curr)

        except:
            args['message'] = 'Пользователю было добавлено {} валюты'.format(curr)
        bot.Replyqueue.put(args)


class Command_SetCurrency(Command_template):
    name = ['setmoney', 'setcurr']
    access = ['admin']
    perm = 'core.currency'
    desc = 'Редактирование кошелька пользователя'

    @staticmethod
    def execute(bot, data, forward=True):
        text = data['text'].split(' ')
        user = text[0]
        curr = text[-1]
        bot.USERS.SetCuttency(user, curr)
        args = {"peer_id": data['peer_id'], "v": "5.60", }
        if forward:
            args.update({"forward_messages": data['message_id']})

        userName = bot.GetUserNameById(user)
        try:
            args['message'] = 'Пользователю {} {} было изменено кол-во валюты на {}'.format(userName['first_name'],
                                                                                            userName['last_name'],
                                                                                            curr)

        except:
            args['message'] = 'Пользователю было изменено кол-во валюты на {}'.format(curr)
        bot.Replyqueue.put(args)
