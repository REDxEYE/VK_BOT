from DataTypes.attachments import attachment
from DataTypes.chat import chat
from DataTypes.doc import doc
from DataTypes.user import user
from DataTypes.photo import photo
from DataTypes.action import action

from utils import ArgBuilder


class LongPoolHistoryMessage:
    def __init__(self):
        self.id = 0
        self.date = 0
        self.out = 0
        self.user_id = 0
        self.title = ''
        self.body = ''
        self.chat_id = 0
        self.chat_active = []
        self.action = action
        self.hasAction = False
        self.fwd_messages = []
        self.hasFwd = False
        self.users_count = 0
        self.admin_id = 0
        self.attachments = []
        self.isChat = False
        self.hasAttachment = False
        self.text = ''
        self.message = ''
        self.args = []
        self.name_args = []
        self.api = None

    def set_api(self,api):
        self.api = api

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
        return {var: vars(self)[var] for var in vars(self)}
        # source_act = Source_act

    def send_back(self, message="", atts=None, fwd=False):
        if atts is None:
            atts = []
        self.api.UserApi.messages.send(**ArgBuilder.Args_message().setmessage(message).setattachment(atts).setforward_messages(self.id if fwd else []).setpeer_id(self.chat_id).AsDict_())


class Updates:
    def __init__(self):
        self.history = []
        self.messages = []
        self.profiles = []
        self.chats = []
        self.new_pts = 0

    def GetUserProfile(self, id: int) -> user:
        """

        Args:
            id (int): User ID

        Returns:
            user
        """
        for user in self.profiles:
            if user.id == id:
                return user

    def GetChat(self, id: int) -> chat:
        """

        Args:
            id (int): Chat ID

        Returns:
            chat
        """
        id = int(id)
        for Chat in self.chats:
            if int(Chat.id) == id:
                return Chat

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
        return {var: vars(self)[var] for var in vars(self)}


class fwd_message:
    def __init__(self):
        self.user_id = 0
        self.date = 0
        self.body = ''
        self.fwd_messages = []
        self.hasFwd = False
        self.hasAttachment = False
        self.depth = 1
        self.attachments = []

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
        return {var: vars(self)[var] for var in vars(self)}


def FillUpdates(resp) -> Updates:
    """

    Args:
        resp (dict): LongPoolHistory response
    """

    def RecirsionFwd(fwd: dict, depth=1) -> fwd_message:
        tFwd = fwd_message()
        tFwd.user_id = fwd['user_id']
        tFwd.date = fwd['date']
        tFwd.body = fwd['body']
        if 'attachments' in fwd:
            tFwd.hasAttachment = True
            for att in fwd['attachments']:
                fAttachment = attachment()
                fAttachment.type = att['type']
                if fAttachment.type == attachment.types.photo:
                    fPhoto = photo.Fill(att['photo'])
                    fAttachment.photo = fPhoto
                if fAttachment.type == attachment.types.doc:
                    fDoc = doc.Fill(att['doc'])
                    fAttachment.doc = fDoc
                tFwd.attachments.append(fAttachment)
        tFwd.depth = depth
        if 'fwd_messages' in fwd:
            tFwd.hasFwd = True
            for fwd2 in fwd['fwd_messages']:
                tFwd.fwd_messages.append(RecirsionFwd(fwd2, depth + 1))
        return tFwd

    a = Updates()
    a.history = resp['history']
    for message in resp['messages']['items']:
        tMessage = LongPoolHistoryMessage()
        tMessage.id = message['id']
        tMessage.date = message['date']
        tMessage.user_id = message['user_id']
        tMessage.title = message['title']
        tMessage.body = message['body']
        if 'attachments' in message:
            tMessage.hasAttachment = True
            for att in message['attachments']:
                tAttachment = attachment()
                tAttachment.type = att['type']
                if tAttachment.type == attachment.types.photo:
                    tPhoto = photo.Fill(att['photo'])
                    tAttachment.photo = tPhoto

                if tAttachment.type == attachment.types.doc:
                    tDoc = doc.Fill(att['doc'])
                    tAttachment.doc = tDoc

                tMessage.attachments.append(tAttachment)
        if 'fwd_messages' in message:
            tMessage.hasFwd = True
            for fwd in message['fwd_messages']:
                tMessage.fwd_messages.append(RecirsionFwd(fwd))
        try:
            tMessage.chat_id = message['chat_id'] + 2000000000
            tMessage.chat_active = message['chat_active']
            tMessage.users_count = message['users_count']
            tMessage.admin_id = message['admin_id']
            tMessage.isChat = True

        except:
            tMessage.chat_id = message['user_id']
            tMessage.chat_active = [message['user_id']]
            tMessage.admin_id = message['user_id']
            tMessage.users_count = 1
        if 'action' in message:
            tAction = action()

            tAction.action = message['action']
            if tAction.action == tAction.types.chat_title_update:
                tAction.action_text = message['action_text']
            if tAction.action == tAction.types.chat_invite_user:
                tAction.action_mid = message['action_mid']
            if tAction.action == tAction.types.chat_kick_user:
                tAction.action_mid = message['action_mid']
            tMessage.action = tAction
            tMessage.hasAction = True

        a.messages.append(tMessage)
        for Userprofile in resp['profiles']:
            tProfile = user.Fill(Userprofile)

            a.profiles.append(tProfile)
        try:
            for c in resp['chats']:
                tChat = chat()
                tChat.id = c['id']
                tChat.type = c['type']
                tChat.title = c['title']
                tChat.admin_id = c['admin_id']
                tChat.users = c['users']
                tChat.photo_50 = c['photo_50']
                tChat.photo_100 = c['photo_100']
                tChat.photo_200 = c['photo_200']
                a.chats.append(tChat)
        except:
            a.chats = []
    return a
