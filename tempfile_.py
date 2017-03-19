import os
import uuid
from os.path import isdir
from random import randint
from zipfile import *


def getpath():
    return os.path.dirname(os.path.abspath(__file__))


class TempFile:
    def __init__(self, data, ras, file=None, NoCache=False):
        try:
            print('temp', os.path.join(getpath(), 'tmp', 'cache.zip'))
            if os.path.isfile(os.path.join(getpath(), 'tmp', 'cache.zip')):
                self.cache = ZipFile(os.path.join(getpath(), 'tmp', 'cache.zip'), 'a', compression=ZIP_LZMA)
            else:
                self.cache = ZipFile(os.path.join(getpath(), 'tmp', 'cache.zip'), 'w', compression=ZIP_LZMA)
            self.NoZip = False
        except:
            self.NoZip = True

        if not isdir('tmp'):
            os.mkdir('tmp')
        self.name = 'tempfile_{}.{}'.format(uuid.uuid4(), ras)
        self.path_ = './tmp/{}'.format(self.name)
        while isdir(self.path_):
            self.name = 'tempfile_{}.{}'.format(uuid.uuid4(), ras)
            self.path_ = './tmp/{}'.format(self.name)
        # print(self.path_)
        self.file = open(self.path_, 'wb')
        self.file.write(data)
        self.file.seek(0)
        if not NoCache:
            self.cachefile(self.path_)
        self.file.close()

    def file_(self):
        return str(self.path_)

    def cachefile(self, path_):
        if self.NoZip:
            return
        self.cache = ZipFile(os.path.join(getpath(), 'tmp', 'cache.zip'), 'a', compression=ZIP_LZMA) if os.path.isfile(
            os.path.join(getpath(), 'tmp', 'cache.zip')) else ZipFile(os.path.join(getpath(), 'tmp', 'cache.zip'), 'w',
                                                                      compression=ZIP_LZMA)
        self.cache.write(path_)

        self.cache.close()
    def rem(self):

        os.remove(self.path_)

    @staticmethod
    def generatePath(ras):
        name = 'tempfile_{}.{}'.format(randint(0, 255), ras)
        path_ = './tmp/{}'.format(name)
        while isdir(path_):
            name = 'tempfile_{}.{}'.format(randint(0, 255), ras)
            path_ = './tmp/{}'.format(name)
        return path_
