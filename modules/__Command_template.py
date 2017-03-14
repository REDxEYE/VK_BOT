class Command_template:
    name = ['Change me']
    access = ['admin']
    desc = "Change me"
    template = "{}, change me"
    perm = 'change.me'

    @staticmethod
    def execute(bot, data, forward=True):
        args = {"peer_id": data['peer_id'], "v": "5.60", "forward_messages": data['message_id']}
        args['message'] = 'Change me'
        bot.Replyqueue.put(args)
