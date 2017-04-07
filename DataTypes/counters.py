class counters:
    def __init__(self):
        self.albums = 0
        self.videos  = 0
        self.audios = 0
        self.photos = 0
        self.notes = 0
        self.friends = 0
        self.groups = 0
        self.online_friends = 0
        self.mutual_friends = 0
        self.user_videos = 0
        self.followers = 0
        self.pages = 0
        self.topics = 0

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self) -> dict:
            return {var: vars(self)[var] for var in vars(self)}
    @staticmethod
    def Fill(data):
        u = counters()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')) and not var == 'AsDict':
                setattr(u,var,data[var])
        return u