class __Command_template:
    name = ['Change me']
    access = ['admin']
    desc = "Change me"
    template = "{}, change me"
    perm = 'change.me'
    cost = 0
    enabled = True
    @staticmethod
    def execute(bot, data, forward=True):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        args['message'] = 'Change me'
        bot.Replyqueue.put(args)



class __Filter_template:

    enabled = True
    name = 'Change me'
    desc = 'Change me'
