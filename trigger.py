import time


class Trigger:
    def __init__(self,cond,callback,onetime = True,timeout = 20,*callbackArgs,**callbackKwArgs):
        """
        :param cond: bool function
        :param callback: callback function
        """
        self.cond = cond
        self.callback = callback
        self.onetime = onetime
        self.timeout = timeout
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
                if time.time()-trigger.timestart > trigger.timeout*1000:
                    self.triggers.remove(trigger)
                    print('Trigger timeout!')
                    trigger.callback(data,result = False)
                if trigger.cond(data):
                    print('triggered!')
                    trigger.callback(data,result = True,*trigger.callbackArgs,**trigger.callbackKwArgs)
                    if trigger.onetime:
                        self.triggers.remove(trigger)
            except:
                continue





