class Module:
    def __init__(self, names: list, perms: str, template: str, desc: str, cost: int,subcommands:dict= {}, access:list = ['all'],funk = None,issubcommad= False):
        self.names = names
        self.funk = funk
        self.perms = perms
        self.access = access
        self.template = template
        self.desc = desc
        self.cost = cost
        self.subcommands = subcommands
        self.issubcommad = issubcommad


    @property
    def hasSubcommands(self):
        return len(self.subcommands)>0
    def __call__(self, *args, **kwargs):
        return self.funk(*args, **kwargs)



class Filter:
    def __init__(self, funk, name: str, desc: str):
        self.funk = funk
        self.name = name
        self.desc = desc
