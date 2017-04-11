class action:
    class types:
        chat_kick_user = 'chat_kick_user'
        chat_title_update = 'chat_title_update'
        chat_invite_user = 'chat_invite_user'
        chat_photo_update = 'chat_photo_update'

    def __init__(self):
        self.action = ''
        self.action_text = ''
        self.action_mid = 0
        self.action_old_text = ''
        self.from_ = 0

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))


    def AsDict(self):
        return {var: vars(self)[var] for var in vars(self)}