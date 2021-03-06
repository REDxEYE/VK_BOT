import importlib
import json
import os
import os.path
import sys
import traceback

from Module_struct import Module, Filter
import CustomPrint

def getpath():
    return os.path.dirname(os.path.abspath(__file__))


class ModuleManager_Namespace:
    names = 'names'
    funk = 'funk'
    perms = 'perms'
    access = 'access'
    template = 'template'
    desc = 'desc'


class ModuleManager:
    def __init__(self):
        self.CONGIFPATH = os.path.join(getpath(),'modules','plugins.json')
        self.ReadConfig()

        self.TYPES = ModuleManager_Namespace
        self.FILTERS = {}
        self.MODULES = []
        self.modules = os.listdir(os.path.join(getpath(), "modules"))
        sys.path.append(os.path.join(getpath(), "modules"))
        for module in self.modules: #type: str
            if not module.startswith("__") and module.endswith('.py'):
                try:
                    module = importlib.import_module(str(module.split(".")[0]))
                except ImportError:
                    print("can't import module " + str(module.split(".")[0]), type_='err')

                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    TB = traceback.format_tb(exc_traceback)
                    print(exc_type, exc_value, ''.join(TB))
                    pass
                    continue
                longest = 0
                toPrint = []

                for class_ in dir(module):

                    if class_.startswith("Filter"):
                        funk = getattr(module, class_)
                        if funk.enabled == False:
                            impModuleStr = ("   ║ skipping {}".format(class_))
                            toPrint.append(impModuleStr)
                            longest = len(impModuleStr) if len(impModuleStr) > longest else longest
                            continue

                        impModuleStr = ("   ║ Importing {}".format(class_))
                        toPrint.append(impModuleStr)
                        longest = len(impModuleStr) if len(impModuleStr) > longest else longest
                        self.FILTERS[funk.name] = Filter(funk, funk.name, funk.desc)

                    if class_.startswith("Command"):
                        if class_ not in self.Config:
                            self.Config[class_] = {'enabled':True}
                        if 'cost' not in self.Config[class_]:
                            self.Config[class_]['cost'] = getattr(module, class_).cost
                        if self.Config[class_]['enabled']:
                            funk = getattr(module, class_)
                            if funk.enabled == False:
                                impModuleStr = ("   ║ skipping {}".format(class_))
                                toPrint.append(impModuleStr)
                                longest = len(impModuleStr) if len(impModuleStr) > longest else longest
                                continue
                            impModuleStr = ("   ║ Importing {}".format(class_))
                            toPrint.append(impModuleStr)
                            longest = len(impModuleStr) if len(impModuleStr) > longest else longest
                            funk.cost = self.Config[class_]['cost']
                            self.MODULES.append(
                                Module(funk, funk.name, funk.perm, funk.access, funk.template, funk.desc, funk.cost))
                        else:
                            impModuleStr = ("   ║ skipping {}".format(class_))
                            toPrint.append(impModuleStr)
                            longest = len(impModuleStr) if len(impModuleStr) > longest else longest
                            continue

                print("Importing module {}\n".format(module.__name__))
                longest += 3
                print_('   ╔{}╗'.format("═" * int(longest / 1)))
                for p in toPrint:
                    Plen = len(p)
                    sp = (longest - Plen) + 4
                    pp = p + " " * sp + "║"
                    print_(pp)
                print_('   ╚{}╝'.format('═' * int(longest / 1)))
        self.WriteConfig()
    def GetModule(self, name):
        """
        :param name - module name
        :rtype Module
        """
        for module in self.MODULES:
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
        comm = self.GetModule(name)
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
            self.Config = json.load(open(self.CONGIFPATH,'r'))
        else:
            self.Config = {}

    def WriteConfig(self):
        if os.path.isfile(self.CONGIFPATH):
            json.dump(self.Config,open(self.CONGIFPATH,'w'), indent=4, sort_keys=True)
        else:
            json.dump(self.Config,open(self.CONGIFPATH,'w'), indent=4, sort_keys=True)

if __name__ == '__main__':
    a = ModuleManager()
    print(a.GetAvailable(['core.*', 'photo.kek']))
