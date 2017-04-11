class chat:
    def __init__(self):
        self.id = 0
        self.type = ''
        self.title = ''
        self.admin_id = 0
        self.users = []
        self.photo_50 = ''
        self.photo_100 = ''
        self.photo_200 = ''

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
        return {var: vars(self)[var] for var in vars(self)}

    @staticmethod
    def Fill(data):
        u = chat()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')) and not var == 'AsDict':
                setattr(u,var,data[var])
        return u