from DataTypes.action import action

class LongPoolMessage:
    def __init__(self):
        self.type = 0
        self.message_id = 0
        self.flags = 0
        self.peer_id = 0
        self.timestamp = 0
        self.subject = ''
        self.message = ''
        self.user_id = 0
        self.attatchments = {}
        self.sourceAct = action

    @property
    def hasAttatchments(self):
        return len(self.attatchments) > 0
    @property
    def hasMessage(self):
        return len(self.message) > 0

    @property
    def hasSourceAct(self):
        return 'source_act' in self.attatchments

    @staticmethod
    def Fill(data:list):
        u = LongPoolMessage()
        u.type = data[0]
        u.message_id = data[1]
        u.flags = data[2]
        u.peer_id = data[3]
        u.timestamp = data[4]
        u.subject = data[5]
        u.message = data[6]
        u.attatchments = data[7]
        if u.hasSourceAct:
            u.sourceAct = action()
            u.sourceAct.action = u.attatchments['source_act']
            if 'source_mid' in u.attatchments:
                u.sourceAct.action_mid = u.attatchments['source_mid']
            u.sourceAct.action_text = u.attatchments['source_text']
            u.sourceAct.action_old_text = u.attatchments['source_old_text']
            u.sourceAct.from_ = u.attatchments['from']
        return u
