import Vk_bot2
from DataTypes.LongPoolHistoryUpdate import LongPoolHistoryMessage,Updates


class C_template:
    name = ['Change me']
    access = ['admin']
    desc = "описание данной команды не указано"
    template = "{botname}, шаблон для данной команды еще не создан"
    perm = 'change.me'
    cost = 0
    enabled = True

    def __init__(self,api:Vk_bot2.Bot):
        self.api = api
        self.sub_init()
    def sub_init(self):
        pass

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        pass


class F_template:

    enabled = True
    name = 'Change me'
    desc = 'Change me'
