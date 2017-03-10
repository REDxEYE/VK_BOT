import copy
import json
import os.path


def getpath():
    return os.path.dirname(os.path.abspath(__file__))


class Actions:
    Remove = 0
    Add = 1
    DefaultPerms = 99


class Status:
    admin = 0
    moder = 1
    user = 99

    @staticmethod
    def getId(id):
        try:
            return vars(Status)[id]
        except:
            raise ('Unknows status')

    @staticmethod
    def getName(id):
        vars_ = vars(Status)
        for var in vars_:
            if vars_[var] == id:
                return var
        else:
            raise ('Unknowd ID')


class UserManager:
    perms = 'perms'
    status = 'status'
    exclude = 'exclude'

    def __init__(self):
        self.Stats = Status
        self.Actions = Actions
        self.DB = self.LoadConfig()
        self.UserTemplate = {'status': 99, 'perms': ['text.*', 'photo.*'], 'warn': 0, 'exclude': []}

    def LoadConfig(self):
        path = getpath()
        if not os.path.exists(path + '\\Users.json'):
            USERS = {}
            return USERS
        with open(path + '\\Users.json', 'r') as config:
            USERS = json.load(config)
        return USERS

    def SaveConfig(self):
        path = getpath()
        with open(path + '\\Users.json', 'w') as config:
            json.dump(self.DB, config, indent=4, sort_keys=True)

    def WriteUser(self, user, status, action=99, *perms):
        user = str(user)
        self.DB[user] = copy.deepcopy(self.UserTemplate)
        self.DB[user]['status'] = Status.getId(status) if status is str else status
        self.WritePerms(user, action, *perms)
        self.SaveConfig()

    def WritePerms(self, user, action, *perms):
        user = str(user)

        if action == Actions.DefaultPerms:
            return
        if user not in self.DB:
            self.WriteUser(user, Status.user)

        if action == Actions.Add:
            print('Writing [ {} ] perms to {}'.format(', '.join(perms), str(user)))
            for perm in perms:
                if perm in self.DB[user][UserManager.exclude]:
                    self.DB[user][UserManager.exclude].remove(perm)
                    continue

                if perm in self.DB[user][UserManager.perms]:
                    continue
                self.DB[user]['perms'].append(perm)

        if action == Actions.Remove:
            print('Removing [ {} ] perms from {}'.format(', '.join(perms), str(user)))
            for perm in perms:

                coreperm = '{}.*'.format(perm.split('.')[0])

                if coreperm in self.DB[user][UserManager.perms]:
                    if perm in self.DB[user][UserManager.exclude]:
                        continue
                    self.DB[user][UserManager.exclude].append(perm)
                    continue

                if perm in self.DB[user][UserManager.perms]:

                    self.DB[user][UserManager.perms].remove(perm)
                else:
                    continue
        self.SaveConfig()

    def GetPerms(self, user):
        user = str(user)
        return self.DB[user][UserManager.perms]

    def HasPerm(self, user, perm):
        coreperm = '{}.*'.format(perm.split('.')[0])
        user = str(user)
        if user not in self.DB:
            self.WriteUser(user, Status.user)
        if perm in self.DB[user][UserManager.exclude]:
            return False

        if coreperm in self.DB[user][UserManager.perms]:
            return True

        return perm in self.DB[user][UserManager.perms]

    def GetStatus(self, user):
        user = str(user)
        if user not in self.DB:
            self.WriteUser(user, Status.user)
        return Status.getName(self.DB[user][UserManager.status])


if __name__ == "__main__":
    a = UserManager()
    # a.WriteUser('test', 'admin', Actions.Add, 'core.Ban')
    # a.WritePerms('test', Actions.Add, 'core.addUser', 'core.removeUser')
    # a.WritePerms('test', Actions.Remove, 'core.removeUser')



    a.WritePerms('test', Actions.Add, 'text.test')

    # a.WriteUser('Red', 'admin')
    # a.WritePerms('Red', Actions.Add, 'core.addUser', 'core.removeUser')
    # print(a.HasPerm('Red', 'core.addUser'))
    # print(a.HasPerm('Red', 'core.addAser'))
    # print(a.HasPerm('Red', 'text.asda'))
