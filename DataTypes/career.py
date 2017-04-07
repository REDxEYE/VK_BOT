class career:
    def __init__(self):
        self.group_id = 0
        self.company = ''
        self.country_id = 0
        self.city_id = 0
        self.city_name = ''
        self.from_ = 0
        self.until = 0
        self.position = ''
    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
            return {var: vars(self)[var] for var in vars(self)}
    @staticmethod
    def Fill(data):
        u = career()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')) and not var == 'AsDict':
                setattr(u,var,data[var])
        return u