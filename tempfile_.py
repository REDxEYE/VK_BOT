import os
from os.path import isdir
from random import randint


def getpath():
    return os.path.dirname(os.path.abspath(__file__))


class TempFile:
    def __init__(self, data, ras):
        if not isdir('tmp'):
            os.mkdir('tmp')
        self.name = 'tempfile_{}.{}'.format(randint(0, 255), ras)
        self.path_ = './tmp/{}'.format(self.name)
        while isdir(self.path_):
            self.name = 'tempfile_{}.{}'.format(randint(0, 255), ras)
            self.path_ = './tmp/{}'.format(self.name)
        # print(self.path_)
        self.file = open(self.path_, 'wb')
        self.file.write(data)
        self.file.seek(0)
        self.file.close()

    def file_(self):
        return str(self.path_)

    def rem(self):
        os.remove(self.path_)
