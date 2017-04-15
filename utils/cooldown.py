import time
import CustomPrint

class cooldown_manager:
    def __init__(self, timeout, limit):
        self.users = {}  # type: dict[str,cooldown]
        self.timeout = timeout
        self.limit = limit

    def adduser(self, user: str):
        user = str(user)
        if user not in self.users:
            self.users[user] = cooldown(self.timeout)
        return self

    def useUser(self, user: str):
        user = str(user)
        print(f'user {user} used command')
        self.users[user].useUser()
        self.users[user].end = time.time() + self.timeout
        return self

    def chechUsers(self):
        print(f"current time : {time.time()}")
        for user in self.users:
            print(f'timeout of user {user} : {self.users[user].end}')
            if time.time() >= self.users[user].end:
                print(f'timeout of user {user} is ended')
                self.users[user].uses = 0
            print(f'user {user} still on waiting for timeout, with {self.users[user].uses} uses')
        return self

    def canUse(self, user):
        user = self.users[str(user)]
        if user.uses <= self.limit:
            user.fakeuse = 0
            return True
        else:
            user.fakeuse +=1
            if user.fakeuse>self.limit:
                user.end+=self.timeout*2
            return False
    def warned(self,user):
        user = self.users[str(user)]
        user.warned = True
    def iswarned(self,user):
        user = self.users[str(user)]
        return  user.warned

class cooldown:
    def __init__(self, timeout):
        self.end = time.time() + timeout
        self.uses = 0
        self.fakeuse = 0
        self.warned = False
    def useUser(self):
        self.uses += 1
