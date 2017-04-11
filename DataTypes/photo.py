class photo:
    def __init__(self):
        self.id = 0
        self.album_id = 0
        self.owner_id = 0
        self.access_key = ''
        self.photo_75 = ''
        self.photo_130 = ''
        self.photo_604 = ''
        self.photo_807 = ''
        self.photo_1280 = ''
        self.photo_2560 = ''
    def GetHiRes(self):
        vars_ = vars(self)
        size = 0
        for var in vars_:
            if var.startswith('photo_') and vars_[var] != '':
                tsize = int(var.split('_')[-1])
                size = tsize if tsize>size else size
        return vars_['photo_{}'.format(size)]
    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
        return {var: vars(self)[var] for var in vars(self)}
    @staticmethod
    def Fill(data):
        u = photo()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('_')) and not var == 'AsDict':
                setattr(u,var,data[var])
        return u

