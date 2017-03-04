import aiml_ as aiml


class Responder:
    def __init__(self, ):
        self.k = aiml.Kernel()
        # self.k.learn("AIMLlib/startup.xml")
        self.k.bootstrap(learnFiles="AIMLlib/startup.xml")
        self.k.bootstrap(learnFiles="AIMLlib/std-1.xml")
        # self.k.respond("load aiml b")
        self.k.setTextEncoding('utf-8')

    def respond(self, msg, id):
        msg = ' '.join(msg.split(' ' if ',' in msg else ' ')[1:])
        ans = self.k.respond(msg, sessionID=id)

        return ans
