

try:
    from .__Command_template import *
except:
    from __Command_template import *



class Command_AddCurrency(C_template):
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



class Command_SetCurrency(C_template):
    name = ['setmoney', 'setcurr']
    access = ['admin']
    perm = 'core.currency'
    desc = 'Редактирование кошелька пользователя'

    @staticmethod
    def execute(bot, data, forward=True):
        text = data['text'].split(' ')
        user = text[0]
        curr = text[-1]
        bot.USERS.SetCurrency(user, curr)
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
class Command_GiveCurr(C_template):
    name = ['скинуть', 'отдолжить']
    access = ['all']
    perm = 'text.giveCurr'
    desc = 'Позволяет передать валюту'

    @staticmethod
    def execute(bot, data, forward=True):
        args = {"peer_id": data['peer_id'], "v": "5.60", }
        if forward:
            args.update({"forward_messages": data['message_id']})
        text = data['text'].split(' ')
        user = text[0]
        curr = text[-1]
        if not bot.USERS.isValid(user):
            args['message'] = 'Неизвестный пользователь. Проверьте правильность указанного вами id'
            bot.Replyqueue.put(args)
            return
        #from
        bot.USERS.pay(str(user), -int(curr))
        #to
        bot.USERS.pay(str(data['user_id']), int(curr))
        userName = bot.GetUserNameById(user)
        try:
            args['message'] = 'Вы перевели {} {} валюты'.format(userName['first_name'], userName['last_name'], curr)

        except:
            args['message'] = 'Вы перевели пользователю {} валюты'.format(curr)
        bot.Replyqueue.put(args)