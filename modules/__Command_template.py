import Vk_bot2
from DataTypes.LongPoolHistoryUpdate import LongPoolHistoryMessage,Updates

import Module_manager_v2

class C_template:

    def __init__(self,api:Vk_bot2.Bot):
        self.api = api
        self.sub_init()
        self.vars:Module_manager_v2.Argument_parser
    def sub_init(self):
        pass

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        pass


class F_template:
    pass
