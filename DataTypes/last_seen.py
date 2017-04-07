class last_seen:
    def __init__(self):
        self.time = 0
        self.platform  = 0
    @staticmethod
    def Fill(data):
        u = last_seen()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')):
                setattr(u,var,data[var])
        return u