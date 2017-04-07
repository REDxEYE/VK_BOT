from DataTypes.photo import photo
class crop:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.x2 = 0
        self.y2 = 0
    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
            return {var: vars(self)[var] for var in vars(self)}
    @staticmethod
    def Fill(data):
        u = crop()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')) and not var == 'AsDict':
                    setattr(u,var,data[var])
        return u

class crop_photo:
    def __init__(self):
        self.photo = photo
        self.crop = crop
        self.rect = crop

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
            return {var: vars(self)[var] for var in vars(self)}

    @staticmethod
    def Fill(data):
        u = crop_photo()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')) and not var == 'AsDict':
                if var == 'chop':
                    setattr(u,var,crop.Fill(data[var]))
                if var == 'photo':
                    setattr(u,var,photo.Fill(data[var]))
                if var == 'rect':
                    setattr(u,var,crop.Fill(data[var]))
                else:
                    setattr(u,var,data[var])
        return u
