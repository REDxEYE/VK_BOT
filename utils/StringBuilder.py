try:
    from overload_fixed import *
except ModuleNotFoundError:
    from utils.overload_fixed import *
class StringBuilder:
    def __init__(self, string=None, sep=''):
        if string is None:
            self._string = []
        else:
            self._string = [string]
        self._sep = sep

    def __str__(self):
        for n,s in enumerate(self._string):
            if isinstance(s,str):
                print('string',s)
                pass
            elif isinstance(s,list):

                print('list',s)
                a = self._string[n:]
                b = self._string[:n+1]
                a.extend(s)
                a.extend(b)
                self._string = a
            else:
                print('unknown',s)
                a = self._string[n:]
                b = self._string[:n + 1]
                a.extend(b)
                self._string = a
        return self._sep.join(self._string)

    def toString(self):
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
    def __iadd__(self, other:str):
        self._string.append(other)
        return self

    @__iadd__.overload
    @signature(list)
    def _(self, other: list):
        self._string.extend(other)
        return self
    def add_list(self,list):
        self._string.extend(list)
    def purge(self):
        self._string = []
if __name__ == '__main__':
    a = StringBuilder(sep='')
    a.append('assd')
    a = a +  'dg'
    a = a + 'asd' + '2asd'
    a = a + ['acc','cvca']

    print(a.toString())