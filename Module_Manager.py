import importlib
import math
import os
import os.path
import sys

from Module_struct import Module, Filter


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
        self.TYPES = ModuleManager_Namespace
        self.FILTERS = {}
        self.MODULES = []
        self.modules = os.listdir(os.path.join(getpath(), "modules"))
        sys.path.append(os.path.join(getpath(), "modules"))
        for module in self.modules:
            if not module.startswith("__"):

                module = importlib.import_module(str(module.split(".")[0]))
                longest = 0
                toPrint = []

                for class_ in dir(module):

                    if class_.startswith("Filter"):
                        funk = getattr(module, class_)

                        impModuleStr = ("   ║ Importing command {}".format(class_))
                        toPrint.append(impModuleStr)
                        longest = len(impModuleStr) if len(impModuleStr) > longest else longest
                        self.FILTERS[funk.name] = Filter(funk, funk.name, funk.desc)

                    if class_.startswith("Command"):
                        funk = getattr(module, class_)

                        impModuleStr = ("   ║ Importing command {}".format(class_))
                        toPrint.append(impModuleStr)
                        longest = len(impModuleStr) if len(impModuleStr) > longest else longest

                        self.MODULES.append(Module(funk, funk.name, funk.perm, funk.access, funk.template, funk.desc))

                print("Importing module {}\n".format(module.__name__))
                longest += 5
                print_('   ╔{}╗'.format("═" * int(longest / 2)))
                for p in toPrint:
                    Plen = len(p)
                    sp = math.floor((longest - Plen)) - 3
                    pp = p + " " * sp + "║"
                    print_(pp)
                print_('   ╚{}╝'.format('═' * int(longest / 2)))

    def GetModule(self, name):
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


if __name__ == '__main__':
    a = ModuleManager()
    print(a.GetAvailable(['core.*', 'photo.kek']))
