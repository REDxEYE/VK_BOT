from DataTypes.city import city
from DataTypes.career import career
from DataTypes.contacts import contacts
from DataTypes.counters import counters
from DataTypes.country import country
from DataTypes.crop_photo import crop_photo
import types
class user(object):

    def __init__(self):
        self.id = 0
        self.first_name = ''
        self.last_name = ''
        self.deactivated = 0
        self.hidden = 0
        self.about = ''
        self.sex = 0
        self.activities = ''
        self.bdate = 'Не указано/скрыто'
        self.blacklisted = 0
        self.blacklisted_by_me = 0
        self.books = []
        self.can_post = 0
        self.can_see_all_posts = 0
        self.can_see_audio = 0
        self.can_send_friend_request = 0
        self.can_write_private_message = 0
        self.career = career
        self.city = city
        self.common_count = 0
        self.connections = 0
        self.contacts = contacts
        self.counters = counters
        self.country = country
        self.crop_photo = crop_photo
        self.domain = ''
        self.first_name_nom = ''
        self.first_name_gen = ''
        self.first_name_dat = ''
        self.first_name_acc = ''
        self.first_name_ins = ''
        self.first_name_abl = ''
        self.followers_count = 0
        self.friend_status = 0
        self.has_mobile = 0
        self.has_photo = 0
        self.home_town = ''
        self.is_favorite = 0
        self.is_friend = 0
        self.is_hidden_from_feed = 0
        self.last_name_nom = ''
        self.last_name_gen = ''
        self.last_name_dat = ''
        self.last_name_acc = ''
        self.last_name_ins = ''
        self.last_name_abl = ''
        self.last_seen = 0

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self)}))

    def AsDict(self):
            return {var: vars(self)[var] for var in vars(self)}

    @staticmethod
    def Fill(data):
        u = user()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')) and (not var == 'AsDict'):
                #print(var,':', data[var])
                if var == 'contacts':
                    setattr(u,var,contacts.Fill(data[var]))

                if var == 'counters':
                    setattr(u,var,counters.Fill(data[var]))

                if var == 'country':
                    setattr(u,var,country.Fill(data[var]))

                if var == 'crop_photo':
                    setattr(u,var,crop_photo.Fill(data[var]))

                if var == 'career':
                    setattr(u,var,career.Fill(data[var]))

                if var == 'city':
                    setattr(u,var,city.Fill(data[var]))
                else:
                    setattr(u,var,data[var])

        return u


