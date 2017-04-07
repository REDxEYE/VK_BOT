class country:
    def __init__(self):
        self.id = 0
        self.title = ''

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
            return {var: vars(self)[var] for var in vars(self)}

    @staticmethod
    def Fill(data):
        u = country()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')) and not var == 'AsDict':
                setattr(u,var,data[var])
        return u