import time
from DataTypes.LongPoolHistoryUpdate import LongPoolHistoryMessage
import threading


class Trigger:
    def __init__(self, cond, callback, onetime=True, timeout=20, infinite=False, *callbackArgs, **callbackKwArgs):
        """

        Args:
            cond (lambda): takes only one param - LongPoolMessage
            callback (function): callback function. Will get all Args and Kwargs
            onetime (bool): is this trigger onetime use?
            timeout (int): timeout in seconds
            infinite (bool): is this trigger infinite? don't affected by onetime and timeout
            *callbackArgs:
            **callbackKwArgs:
        """
        self.cond = cond
        self.callback = callback
        self.onetime = onetime
        self.timeout = timeout
        self.infinite = infinite
        self.timestart = time.time()
        self.callbackArgs = callbackArgs
        self.callbackKwArgs = callbackKwArgs

    def __str__(self):
        return str(dict({var: str(vars(self)[var]) for var in vars(self) if vars(self)[var] != None}))

    def AsDict(self):
        return {var: vars(self)[var] for var in vars(self) if vars(self)[var] != None}


class TriggerHandler:
    def __init__(self):
        self.triggers = []

    def addTrigger(self, *trigger: Trigger):

        """

        Args:
            *trigger (Trigger):
        """
        print('Trigger registered!')
        self.triggers.extend(trigger)

    def processTriggers(self, data:LongPoolHistoryMessage):
        """

        Args:
            data (LongPoolHistoryMessage):
        """
        for n, trigger in enumerate(self.triggers):

            if time.time() - trigger.timestart > trigger.timeout and not trigger.infinite:
                self.triggers.remove(trigger)
                trigger.callback(data, result=False)
            if trigger.cond(data):
                print('Triggered, calling callback')
                print(trigger.callbackArgs, trigger.callbackKwArgs)
                LocalcallbackArgs = list(trigger.callbackArgs)
                LocalcallbackArgs.append(data)
                trigger.callbackKwArgs['result'] = True
                print(LocalcallbackArgs, trigger.callbackKwArgs)
                th = threading.Thread(target=trigger.callback, args=LocalcallbackArgs, kwargs=trigger.callbackKwArgs)
                th.setName('Trigger Callback thread {}'.format(n))
                th.start()
                th.join()
                th.isAlive = False
                if trigger.onetime and not trigger.infinite:
                    self.triggers.remove(trigger)

    @property
    def count(self):
        return len(self.triggers)

    @property
    def HasActive(self):
        return any(self.triggers)
