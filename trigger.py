import time
from DataTypes.LongPoolUpdate import LongPoolMessage

class Trigger:
    def __init__(self,cond,callback,onetime = True,timeout = 20,infinite = False,*callbackArgs,**callbackKwArgs):

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

    def addTrigger(self,*trigger:Trigger):

        """

        Args:
            *trigger (Trigger):
        """
        print('Trigger registered!')
        self.triggers.extend(trigger)

    def processTriggers(self,data):
        """

        Args:
            data (LongPoolMessage):
        """
        for trigger in self.triggers:
            try:
                if time.time()-trigger.timestart > trigger.timeout:
                    self.triggers.remove(trigger)
                    trigger.callback(data,result = False)
                if trigger.cond(data):
                    print('Triggered, calling callback')
                    trigger.callback(data,result = True,*trigger.callbackArgs,**trigger.callbackKwArgs)
                    if trigger.onetime and not trigger.infinite:
                        self.triggers.remove(trigger)
            except:
                continue





