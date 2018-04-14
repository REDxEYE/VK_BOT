import logging
import datetime
import threading
import time
import sys


class ConsoleLogger():
    default_time_format = '%Y-%m-%d %H:%M:%S'
    @staticmethod
    def getData(date:datetime.datetime):
        return "{day}.{mouth}.{year}".format(day=date.day,
                                             mouth=date.month,
                                             year=date.year,)


    def __init__(self,name):
        self.logger = logging.getLogger(name)
        self.format = '[{asctime}] - [{name} - {threadName}]: {levelname} - {message}'
        logging.basicConfig(filename= 'VK_LOG_{}_{}.log'.format(name,self.getData(datetime.datetime.today())),style='{',format=self.format,filemode='a')
    @property
    def getCallser(self):
        return sys._getframe(3).f_code.co_name


    def log(self, level, msg):
        msgnew = []
        # print(msg)
        for t in msg:

            if isinstance(t, tuple):
                t = list(t)
            else:
                t = str(t)
            msgnew.append(t)
        msg = msgnew
        # print(msg)
        msg = "[{}]: {}".format(self.getCallser,' '.join(msg))
        self.logger.log(level=level,msg = msg)

        t = time.strftime(self.default_time_format)
        print(self.format.format(asctime=t,name =self.logger.name,threadName=threading.current_thread().name,levelname=logging._levelToName[level],message=msg))

    def warn(self,*msg):
        self.log(logging.WARN,msg)
    def debug(self,*msg):
        self.log(logging.DEBUG,msg)
    def error(self,*msg):
        self.log(logging.ERROR,msg)
    def critical(self,*msg):
        self.log(logging.CRITICAL,msg)
    def info(self,*msg):
        self.log(logging.INFO,msg)


    def setLevel(self,lvl):
        self.setLevel(lvl)


if __name__ == '__main__':
    b = ConsoleLogger('Test')
    b.log(logging.WARN,'test')
