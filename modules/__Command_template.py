class C_template:
    name = ['Change me']
    access = ['admin']
    desc = "описание данной команды не указано"
    template = "{botname}, шаблон для данной команды еще не создан"
    perm = 'change.me'
    cost = 0
    enabled = True
    @staticmethod
    def execute(bot, data, forward=True):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        args['message'] = 'Change me'
        bot.Replyqueue.put(args)



class F_template:

    enabled = True
    name = 'Change me'
    desc = 'Change me'
