from DataTypes.city import city
from DataTypes.country import country
from DataTypes.counters import counters

class ban_info:
    def __init__(self):
        self.end_date = None
        self.comment = None


class contacts_group:
    def __init__(self):
        self.user_id = None
        self.desc = None
        self.phone = None
        self.email = None
    @staticmethod
    def Fill(data):
        """

        Args:
            data (dict):
        Returns:
            contacts_group
        """
        u = contacts_group()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')) and not var == 'AsDict':
                setattr(u,var,data[var])
        return u
    # def __str__(self):
    #     return str(dict({var: str(vars(self)[var]) for var in vars(self) if vars(self)[var] != None}))
    #
    # def AsDict(self):
    #     return {var: vars(self)[var] for var in vars(self) if vars(self)[var] != None}
class group:
    def __init__(self):
        self.id = None
        self.name = None
        self.screen_name = None
        self.is_closed = None
        self.deactivated = None
        self.is_admin = None
        self.admin_level = None
        self.is_member = None
        self.invited_by = None
        self.type = None
        self.has_photo = None
        self.photo_50 = None
        self.photo_100 = None
        self.photo_200 = None
        self.activity = None
        self.age_limits = None
        self.ban_info = None
        self.can_create_topic = None
        self.can_message = None
        self.can_post = None
        self.can_see_all_posts = None
        self.can_upload_doc = None
        self.can_upload_video = None
        self.city = city
        self.contacts = contacts_group
        self.city = None
        self.counters = counters
        self.country = country
        self.description = None
        self.fixed_post = None
        self.is_favorite = None
        self.is_hidden_from_feed = None
        self.is_messages_allowed = None
        self.member_status = None
        self.members_count = None

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self) if vars(self)[var] != None}))

    def AsDict(self):
        return {var: vars(self)[var] for var in vars(self) if vars(self)[var] != None}

    @staticmethod
    def Fill(data):
        u = group()
        vars_ = vars(u)
        for var in vars_:
            if (var in data) and (not var.startswith('__')):
                if var == 'counters':
                    setattr(u, var, counters.Fill(data[var]))
                elif var == 'country':
                    setattr(u, var, country.Fill(data[var]))
                elif var == 'contacts':
                    t = []
                    for cont in data[var]:
                        t.append(contacts_group.Fill(cont))

                    setattr(u, var, t)


                elif var == 'city':
                    setattr(u, var, city.Fill(data[var]))

                else:
                    setattr(u, var, data[var])
        return u

