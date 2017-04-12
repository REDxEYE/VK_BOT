try:
    from .__Command_template import *
except:
    from __Command_template import *





class Command_SetStatus(C_template):
    name = ["status"]
    access = ["admin"]
    desc = "Устанавливает права на пользователя"
    perm = 'core.SetStatus'


    @staticmethod
    def execute(bot:Vk_bot2.Bot, data:LongPoolHistoryMessage, Updates:Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        print('Adduser: ', data)
        bb = data.text.split(' ')
        user = bb[0]
        stat = bb[1]
        print(user, stat)
        bot.USERS.SetStatus(user, stat)

        userName = bot.GetUserNameById(user)
        try:
            args['message'] = f'Пользователю {userName.Name} был установлен статус {stat}'

        except:
            args['message'] = f'Пользователю были даны следующие права [ {stat} ]'
        # self.Reply(self.UserApi, MArgs)
        bot.Replyqueue.put(args)
        bot.SaveConfig()


class Command_RemovePerms(C_template):
    name = ["rperms"]
    access = ["admin"]
    desc = "Снимает права у пользователя"
    perm = 'core.Removeperms'

    @staticmethod
    def execute(bot:Vk_bot2.Bot, data:LongPoolHistoryMessage, Updates:Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        print('Adduser: ', data)
        bb = data.text.split(' ')
        user = bb[0]
        perms = bb[1:]
        bot.USERS.WritePerms(user, bot.USERS.Actions.Remove, *perms)

        userName = bot.GetUserNameById(int(user))
        try:
            args['message'] = f'Пользователю {userName.Name} были сняты следующие права [ {", ".join(perms)} ]'
        except:
            args['message'] = f'Пользователю были сняты следующие права [ {", ".join(perms)} ]'
        # self.Reply(self.UserApi, MArgs)
        bot.Replyqueue.put(args)
        bot.SaveConfig()


class Command_WritePerms(C_template):
    name = ["perms"]
    access = ["admin"]
    desc = "Устанавливает права на пользователя"
    perm = 'core.Writeperms'

    @staticmethod
    def execute(bot:Vk_bot2.Bot, data:LongPoolHistoryMessage, Updates:Updates, forward=True):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        print('Adduser: ', data)
        bb = data.text.split(' ')
        user = bb[0]
        perms = bb[1:]
        bot.USERS.WritePerms(user, bot.USERS.Actions.Add, *perms)

        userName = bot.GetUserNameById(user)
        try:
            args['message'] = f'Пользователю {userName.Name} были даны следующие права [ {", ".join(perms)} ]'

        except:
            args['message'] = f'Пользователю были даны следующие права [ {", ".join(perms)} ]'
        # self.Reply(self.UserApi, MArgs)
        bot.Replyqueue.put(args)
        bot.SaveConfig()
