from Module_manager_v2 import ModuleManager

try:
    from .__Command_template import *
except:
    from __Command_template import *
from utils import ArgBuilder



@ModuleManager.command(names=["status"], perm='core.SetStatus', desc="Устанавливает права на пользователя")
class Command_SetStatus(C_template):
    name = ["status"]
    access = ["admin"]
    desc = "Устанавливает права на пользователя"
    perm = 'core.SetStatus'


    
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        print('Adduser: ', data)
        bb = data.text.split(' ')
        user = bb[0]
        stat = bb[1]
        print(user, stat)
        self.api.USERS.SetStatus(user, stat)

        userName = self.api.GetUserNameById(user)
        try:
            args['message'] = f'Пользователю {userName.Name} был установлен статус {stat}'

        except:
            args['message'] = f'Пользователю были даны следующие права [ {stat} ]'
        # self.Reply(self.UserApi, MArgs)
        self.api.Replyqueue.put(args)
        self.api.SaveConfig()

@ModuleManager.command(names=["rperms"], perm='core.Removeperms', desc="Снимает права у пользователя")
class Command_RemovePerms(C_template):
    name = ["rperms"]
    access = ["admin"]
    desc = "Снимает права у пользователя"
    perm = 'core.Removeperms'

    
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = {"peer_id": data.chat_id, "v": "5.60", "forward_messages": data.id}
        print('Adduser: ', data)
        bb = data.text.split(' ')
        user = bb[0]
        perms = bb[1:]
        self.api.USERS.WritePerms(user, self.api.USERS.Actions.Remove, *perms)

        userName = self.api.GetUserNameById(int(user))
        try:
            args['message'] = f'Пользователю {userName.Name} были сняты следующие права [ {", ".join(perms)} ]'
        except:
            args['message'] = f'Пользователю были сняты следующие права [ {", ".join(perms)} ]'
        # self.Reply(self.UserApi, MArgs)
        self.api.Replyqueue.put(args)
        self.api.SaveConfig()

@ModuleManager.command(names=["perms"], perm='core.Writeperms', desc="Устанавливает права на пользователя",subcommands=['add','rm'])
class Command_WritePerms(C_template):
    name = ["perms"]
    access = ["admin"]
    desc = "Устанавливает права на пользователя"
    perm = 'core.Writeperms'

    
    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setpeer_id(data.chat_id).setforward_messages(data.id)
        userperms = self.api.USERS.GetPerms(data.user_id)
        userstatus = self.api.USERS.GetStatus(data.user_id)
        a = "\n".join(userperms)
        args['message'] = f'Ваши права :\n{a}\n'
        self.api.Replyqueue.put(args)

    def add(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setforward_messages(data.id).setpeer_id(data.chat_id)
        print('Adduser: ', data)
        bb = data.args
        if data.hasFwd:
            user = str(data.fwd_messages[0].user_id)
            perms = bb[0:]
        else:
            user = bb[0]
            perms = bb[1:]
        print('user ',user)
        if not user.isdigit():
            return False

        self.api.USERS.WritePerms(user, self.api.USERS.Actions.Add, *perms)

        userName = self.api.GetUserNameById(user)
        try:
            args['message'] = f'Пользователю {userName.Name} были даны следующие права [ {", ".join(perms)} ]'

        except:
            args['message'] = f'Пользователю были даны следующие права [ {", ".join(perms)} ]'
        # self.Reply(self.UserApi, MArgs)
        self.api.Replyqueue.put(args)
        self.api.SaveConfig()
    def rm(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        args = ArgBuilder.Args_message().setforward_messages(data.id).setpeer_id(data.chat_id)
        print('Adduser: ', data)
        bb = data.args
        if data.hasFwd:
            user = str(data.fwd_messages[0].user_id)
            perms = bb[0:]
        else:
            user = bb[0]
            perms = bb[1:]
        print('user ',user)
        if not user.isdigit():
            return False

        self.api.USERS.WritePerms(user, self.api.USERS.Actions.Remove, *perms)

        userName = self.api.GetUserNameById(user)
        try:
            args['message'] = f'Пользователю {userName.Name} были сняты следующие права [ {", ".join(perms)} ]'
        except:
            args['message'] = f'Пользователю были сняты следующие права [ {", ".join(perms)} ]'
        # self.Reply(self.UserApi, MArgs)
        self.api.Replyqueue.put(args)
        self.api.SaveConfig()