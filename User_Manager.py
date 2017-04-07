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
    Ян = 9999
    Супер_Зуйков = 621
    UberAdmin = -1

    @staticmethod
    def getId(id):
        try:
            print(id)
            return vars(Status)[id]
        except:
            raise Exception('Unknows status: {}'.format(id))

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
    currency = 'currency'
    cache = 'cache'

    def __init__(self):
        self.Stats = Status
        self.Actions = Actions
        self.DB = self.LoadConfig()
        self.UserTemplate = {'status': 99, 'perms': ['text.*', 'photo.*'], 'warn': 0, 'exclude': [], 'currency': 100}

    def LoadConfig(self):
        path = getpath()
        if not os.path.exists(os.path.join(path, 'Users.json')):
            USERS = {}
            return USERS
        with open(os.path.join(path, 'Users.json'), 'r') as config:
            USERS = json.load(config)
        return USERS

    def SaveConfig(self):
        path = getpath()
        with open(os.path.join(path, 'Users.json'), 'w') as config:
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

    def GetUser(self,user):
        user = str(user)
        if self.isValid(user):
            return self.DB[user]
        else:
            raise Exception('NOT VALID USER')

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

    def SetStatus(self, user, status):
        user = str(user)
        if user not in self.DB:
            self.WriteUser(user, status)
        else:
            self.DB[user][UserManager.status] = Status.getId(status)
            self.SaveConfig()
        return

    def GetStatusId(self, user):
        user = str(user)
        if user not in self.DB:
            self.WriteUser(user, Status.user)
        return self.DB[user][UserManager.status]

    def GetCurrency(self, user):
        user = str(user)
        return self.DB[user][UserManager.currency]

    def UpdateCuttency(self, user, amount):
        amount = int(amount)
        self.DB[user][UserManager.currency] += amount
        self.SaveConfig()

    def pay(self, user: str, amount: int):
        amount = int(amount)
        user = str(user)
        self.DB[user][UserManager.currency] -= amount
        self.SaveConfig()

    def isValid(self,user:str):
        return user in self.DB

    def SetCurrency(self, user, ammount):
        ammount = int(ammount)
        self.DB[user][UserManager.currency] = ammount
        self.SaveConfig()

    def _update(self):
        for user, data in self.DB.items():
            if 'currency' not in data:
                data.update({'currency': 100})
            print(data)
            self.DB[user] = data
        self.SaveConfig()

    def cacheUser(self,user,data):
        user = str(user)
        self.DB[user][UserManager.cache] = data
        self.SaveConfig()
    def isCached(self,user):
        user = str(user)
        if self.isValid(user):
            return UserManager.cache in self.DB[user]
        else:
            self.WriteUser(user, Status.user)
            return self.isCached(user)
    def getCache(self,user:str):
        user = str(user)
        return self.DB[user][UserManager.cache]
    def IsValid(self,user):
        user = str(user)
        return user in self.DB
if __name__ == "__main__":
    a = UserManager()
    a._update()
