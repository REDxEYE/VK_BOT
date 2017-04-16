
from utils.overload_fixed import *

class StringBuilder:
    def __init__(self, string=None, sep=''):
        if string is None:
            string = []
        self._string = string
        self._sep = sep

    def __str__(self):
        return self._sep.join(self._string)

    def toSting(self):
        return self.__str__()

    def append(self, data):
        self._string.append(data)
        return self

    @Overload
    @signature(str)
    def __add__(self, other):
        self._string.append(other)
        return self

    @__add__.overload
    @signature(list)
    def _(self, other: list):
        self._string.extend(other)
        return self

    @Overload
    @signature(str)
    def __iadd__(self, other):
        self._string.append(other)
        return self

    @__iadd__.overload
    @signature(list)
    def _(self, other: list):
        self._string.extend(other)
        return self


if __name__ == '__main__':
    a = StringBuilder(sep='')
    a.append('assd')
    a = a +  'dg'
    a = a + 'asd' + '2asd'
    a = a + ['acc','cvca']
    print(a)