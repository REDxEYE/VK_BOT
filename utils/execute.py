import re

class VkFunction:

    def __init__(self,code):
        self.args_template = re.compile('\{(\w+)\}')
        self.code = code # type: str


    def sanityCheck(self,args):
        vars_ = self.args_template.findall(self.code)
        if len(args) >= len(vars_):
            return
        else:
            raise Exception(f'Missing args: {[var for var in vars_ if var not in args]}')

    def __call__(self, kvars):
        self.sanityCheck(kvars)
        return {'code':self.code.format(**kvars).replace("'","\""),'v':'5.63'}


if __name__ == "__main__":
    a = VkFunction('return API.{method}({values})["items"]@.{keys};')

    print(a({'method':'Wall','values':['asd'],'keys':'test'}))
