import os.path
from shutil import rmtree
from sys import exit

from os import execl


def getpath():
    return os.path.dirname(os.path.abspath(__file__))
from subprocess import Popen

execl('python3 '+os.path.join(getpath(),"Vk_bot2.py"), shell=True) # go back to your program

exit("exit to restart the true program")