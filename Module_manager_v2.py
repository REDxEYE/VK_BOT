import importlib
import inspect
import os.path
import traceback
import ujson

import sys


import Module_struct
from Vk_bot2 import Bot
from utils.utils import getpath
import CustomPrint
class ModuleManager:
    MODULES = []  # type: list[Module_struct.Module]
    FILTERS = {} # type: dict[str,Module_struct.Filter]
    api = None


    def __init__(self, api:Bot):
        self.setApi(api)
        self.CONGIFPATH = os.path.join(api.ROOT, 'modules', 'plugins.json')
        self.ReadConfig()
        self.mods = [] # type: list[Module_struct.Filter]
        self.loadModules()

        print(f'LOADED {len(self.MODULES)} command and {len(self.FILTERS)} filters ',type_ = 'MODULE LOADER')




        self.WriteConfig()

    def loadModules(self):
        modules = os.listdir(os.path.join(self.api.ROOT, "modules"))
        sys.path.append(os.path.join(self.api.ROOT, "modules"))
        for module_ in modules:  # type: str
            if not module_.startswith("__") and module_.endswith('.py'):
                try:
                    importlib.import_module(str(module_.split(".")[0]))
                except:
                    print("can't import module " + str(module_.split(".")[0]), type_='err')
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    TB = traceback.format_tb(exc_traceback)
                    CustomPrint.print_(exc_type, exc_value, traceback.print_tb(exc_traceback))
                    continue

    @classmethod
    def command(cls, names=["Change me"], perm='core.dev', desc='В разработке',
                template='{botname}, данная команда в разработке', cost=0,subcommands = []):
        def loader(funk):
            print(f'registered command "{names[0]}"')
            f = funk(cls.api)
            subs = {}
            for sub in subcommands:
                subs[sub]=Module_struct.Module(names=[sub], perms=perm, desc=desc, template=template, cost=cost, funk=getattr(f,sub),issubcommad=True)
            cls.MODULES.append(Module_struct.Module(names=names, perms=perm, desc=desc, template=template, cost=cost, funk=f,subcommands= subs))
        return loader


    @classmethod
    def Filter(cls, name='changeme', desc='В разработке',):
        def loader(funk):
            print(f'registered command "{name}"')
            cls.FILTERS[name] = Module_struct.Filter(funk = funk,name=name,desc=desc)
            return funk
        return loader

    @property
    def getModules(self):
        return self.MODULES

    @classmethod
    def setApi(cls, api):
        cls.api = api


    def GetModule(self, name,args:list = None):
        """
        :param name - module name
        :rtype Module
        """
        for module in self.MODULES:
            if args is not None:
                if module.hasSubcommands and any(args):
                    print(args)
                    if args[0] in module.subcommands:
                        c =args[0]
                        args.remove(args[0])
                        return module.subcommands[c]
            if name in module.names:
                return module

    def GetFilter(self, name):
        return self.FILTERS[name]

    def isValid(self, name):
        for module in self.MODULES:
            if name in module.names:
                return True
        return False

    def CanAfford(self, user_curr, name):
        comm = self.GetModule(name,None)
        if user_curr > comm.cost:
            return True
        else:
            return False

    def GetAvailable(self, perms):
        Available = []
        for perm in perms:
            core, sec = perm.split('.')
            for module in self.MODULES:
                ModPerm = module.perms
                ModCore, ModSec = ModPerm.split('.')
                if core == ModCore and sec == ModSec:
                    Available.append(module)
                elif core == ModCore and sec == '*':
                    Available.append(module)
                else:
                    continue
        return Available


    def ReadConfig(self):
        if os.path.isfile(self.CONGIFPATH):
            self.Config = ujson.load(open(self.CONGIFPATH,'r'))
        else:
            self.Config = {}

    def WriteConfig(self):
        if os.path.isfile(self.CONGIFPATH):
            ujson.dump(self.Config,open(self.CONGIFPATH,'w'), indent=4, sort_keys=True)
        else:
            ujson.dump(self.Config,open(self.CONGIFPATH,'w'), indent=4, sort_keys=True)



if __name__ == '__main__':
    a = ModuleManager(None)
    print(a.MODULES)