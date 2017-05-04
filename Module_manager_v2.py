import distutils.util
import importlib
import inspect
import os.path
import traceback
import ujson

import sys
from copy import copy

import Module_struct
from Vk_bot2 import Bot
from utils.utils import getpath
import CustomPrint


class Argument_parser:
    def __init__(self):
        self.vars_ = []

    def add(self, key, defval='', desc='None', required=False):
        self.vars_.append(arg(key=key, desc=desc, required=required, defval=defval))
        # print(self.vars_)
        self.__dict__[key] = defval
        return self

    def parse(self, string: str):
        t = string.strip().split(':')
        key = t[0]
        data = ':'.join(t[1:])
        for var in self.vars_:  # type: arg
            if var.key == key:

                if type(var.defval) is bool:
                    data = distutils.util.strtobool(data)
                print(f'found arg {var.key} with val {data}')
                self.__dict__[var.key] = type(var.defval)(data)

    @property
    def get_unfilled(self):
        return [var for var in self.vars_ if (self.__dict__[var.key] == var.defval and var.required)]

    @property
    def has_missing(self):
        return any(self.get_unfilled)

    @property
    def get_vars(self):
        return self.vars_


class Workside:
    both = 0
    chat = 1
    pm = 2


class arg:
    def __init__(self, key, desc, required=False, defval=None):
        self.key = key
        self.desc = desc
        self.required = required
        self.defval = defval


class ModuleManager:
    MODULES = []  # type: list[Module_struct.Module]
    FILTERS = {}  # type: dict[str,Module_struct.Filter]
    api = None

    def __init__(self, api: Bot):
        self.setApi(api)
        self.CONGIFPATH = os.path.join(api.ROOT, 'modules', 'plugins.json')
        self.Config = {}
        self.ReadConfig()
        self.mods = []  # type: list[Module_struct.Filter]
        self.loadModules()

        print(f'LOADED {len(self.MODULES)} command and {len(self.FILTERS)} filters ', type_='MODULE LOADER')

        self.WriteConfig()

    def loadModules(self, reload=False):
        path = os.path.join(self.api.ROOT, "modules")
        modules = os.listdir(path)
        sys.path.append(path)
        for module_ in modules:  # type: str
            if not module_.startswith("__") and module_.endswith('.py'):
                try:
                    if reload:

                        for n, mod in enumerate(self.MODULES):
                            del self.MODULES[n]
                        for f in copy(self.FILTERS):
                            del self.FILTERS[f]
                        importlib.reload(sys.modules[str(module_.split(".")[0])])
                    else:
                        importlib.import_module(str(module_.split(".")[0]))
                except:
                    print("can't import module " + str(module_.split(".")[0]), type_='err')
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    TB = traceback.format_tb(exc_traceback)
                    CustomPrint.print_(exc_type, exc_value, traceback.print_tb(exc_traceback))
                    continue

    @classmethod
    def command(cls, names=["Change me"], perm='core.dev', desc='В разработке',
                template='{botname}, данная команда в разработке', cost=0, subcommands=[]):
        def loader(funk) -> object:
            print(f'registered command "{names[0]}"')
            f = funk(cls.api)
            subs = {}
            for sub in subcommands:
                subs[sub] = Module_struct.Module(names=[sub], perms=perm, desc=desc, template=template, cost=cost,
                                                 funk=getattr(f, sub), issubcommad=True)
            cls.MODULES.append(
                Module_struct.Module(names=names, perms=perm, desc=desc, template=template, cost=cost, funk=f,
                                     subcommands=subs))
            return f

        return loader

    @staticmethod
    def side(side=Workside.both):
        def loader(obj: object):
            obj.side = side
            return obj

        return loader

    @staticmethod
    def argument(argname, defvalue, desc, required):

        def loader(cls_: object):
            if not hasattr(cls_, 'vars'):
                cls_.vars = Argument_parser().add(key=argname, defval=defvalue, desc=desc, required=required)
            else:
                cls_.vars.add(key=argname, defval=defvalue, desc=desc, required=required)
            return cls_

        return loader

    @classmethod
    def Filter(cls, name='changeme', desc='В разработке', ):
        def loader(funk):
            print(f'registered command "{name}"')
            cls.FILTERS[name] = Module_struct.Filter(funk=funk, name=name, desc=desc)
            return funk

        return loader

    @property
    def getModules(self):
        return self.MODULES

    @classmethod
    def setApi(cls, api):
        cls.api = api

    def GetModule(self, name, args: list = None):
        """
        :param name - module name
        :param args - command args
        :rtype Module

        Args:
            name (str): module name 
            args (list): command args
        """
        for module_ in self.MODULES:
            if args is not None:
                if module_.hasSubcommands and any(args):
                    print(args)
                    if args[0] in module_.subcommands:
                        c = args[0]
                        args.remove(args[0])
                        return module_.subcommands[c]
            if name in module_.names:
                return module_

    def GetFilter(self, name):
        return self.FILTERS[name]

    def isValid(self, name):
        for module_ in self.MODULES:
            if name in module_.names:
                return True
        return False

    def CanAfford(self, user_curr, name):
        comm = self.GetModule(name, None)
        if user_curr > comm.cost:
            return True
        else:
            return False

    def GetAvailable(self, perms):
        Available = []
        for perm in perms:
            core, sec = perm.split('.')
            for module_ in self.MODULES:
                ModPerm = module_.perms
                ModCore, ModSec = ModPerm.split('.')
                if core == ModCore and sec == ModSec:
                    Available.append(module_)
                elif core == ModCore and sec == '*':
                    Available.append(module_)
                else:
                    continue
        return Available

    def ReadConfig(self):
        if os.path.isfile(self.CONGIFPATH):
            self.Config = ujson.load(open(self.CONGIFPATH, 'r'))
        else:
            self.Config = {}

    def WriteConfig(self):
        if os.path.isfile(self.CONGIFPATH):
            ujson.dump(self.Config, open(self.CONGIFPATH, 'w'), indent=4, sort_keys=True)
        else:
            ujson.dump(self.Config, open(self.CONGIFPATH, 'w'), indent=4, sort_keys=True)


if __name__ == '__main__':
    a = ModuleManager(None)
    print(a.MODULES)
