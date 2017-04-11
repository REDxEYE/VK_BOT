from DataTypes.photo import photo
from DataTypes.doc import doc
class attachment:

    class types:
        photo = 'photo'
        video = 'video'
        audio = 'audio'
        doc = 'doc'
        link = 'link'
        market = 'market'
        market_album = 'market_album'
        wall = 'wall'
        wall_reply = 'wall_reply'
        sticker = 'sticker'
        gift = 'gift'

    def __init__(self):
        self.type = ''
        self.photo = photo
        self.video = None
        self.audio = None
        self.doc = doc
        self.link = None
        self.market = None
        self.market_album = None
        self.wall = None
        self.wall_reply = None
        self.sticker = None
        self.gift = None
    def GetOwnerAndId(self,type) ->(int,int,str):
        return vars(self)[type].owner_id,vars(self)[type].id, vars(self)[type].access_key if 'access_key' in vars(vars(self)[type]) else None

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))
    def AsDict(self):
        return {var: vars(self)[var] for var in vars(self)}

