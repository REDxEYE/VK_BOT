import time

class Trigger:
    def __init__(self,cond,callback,onetime = True,timeout = 20,infinite = False,*callbackArgs,**callbackKwArgs):
        """
        :param cond: bool function
        :param callback: callback function
        """
        self.cond = cond
        self.callback = callback
        self.onetime = onetime
        self.timeout = timeout
        self.infinite = infinite
        self.timestart = time.time()
        self.callbackArgs = callbackArgs
        self.callbackKwArgs = callbackKwArgs
class TriggerHandler:
    def __init__(self):
        self.triggers = []

    def addTrigger(self,*trigger:Trigger):
        """
        :param trigger: Trigger class instance
        """
        self.triggers.extend(trigger)

    def processTriggers(self,data):
        for trigger in self.triggers:
            try:
                print(data,trigger.cond(data))
                print(time.time()-trigger.timestart)
                if time.time()-trigger.timestart > trigger.timeout:
                    self.triggers.remove(trigger)
                    trigger.callback(data,result = False)
                if trigger.cond(data):
                    trigger.callback(data,result = True,*trigger.callbackArgs,**trigger.callbackKwArgs)
                    if trigger.onetime and not trigger.infinite:
                        self.triggers.remove(trigger)
            except:
                continue





