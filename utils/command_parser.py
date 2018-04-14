import re

import ConsoleLogger
LOGGER = ConsoleLogger.ConsoleLogger('CommandParser')
class Command_parser:
    def __init__(self, prefix, name_pattern):
        self.prefix: str = prefix
        self.name_pattern: re._pattern_type = re.compile(name_pattern)

    def tokenize(self,message:str):
        lines = message.strip().splitlines(True)
        for line in lines:
            for word in line.split(" "):
                # word = word.strip(" .,'\"")
                yield word


    def parse(self, message: str):
        named_args = []
        single_args = []
        command = None
        tokens = self.tokenize(message)
        name = next(tokens)
        if name == self.prefix or any(self.name_pattern.findall(name)):
            command = next(tokens)
            while True:
                try:
                    fst = next(tokens)
                    sec = next(tokens)
                    print([fst,sec])
                    if sec.endswith("\n"):
                        named_args.append((fst.strip("\n"),sec.strip("\n")))
                    elif fst.endswith('\n'):
                        named_args.append((sec.strip("\n"), fst.strip("\n")))
                    else:
                        single_args.append(fst)
                        single_args.append(sec)
                except StopIteration:
                    break
        return command,named_args, single_args, message[len(name):].lstrip(' ,.')[len(command):].lstrip(' \n')
        # if message.startswith(self.prefix):
        #     args: list = message[len(self.prefix):].split(' ')
        #     command: str = args[0].strip()
        #     args: list = args[1:]
        #     text: str = message[len(self.prefix) + len(command):].strip(' ')
        #     return command, args, text
        # elif self.name_pattern.findall(message):
        #     args: list = self.name_pattern.split(message)[-1].split(' ')
        #     command: str = args[0]
        #     args: str = args[1:]
        #     text: str = ' '.join(args)
        #     return command, args, text

    def set_prefix(self,prefix):
        self.prefix = prefix

    def check_for_command(self,message):
        # LOGGER.info(message,message.startswith(self.prefix+" "),self.name_pattern.findall(message))
        return message.startswith(self.prefix+" ") or self.name_pattern.findall(message)

if __name__ == '__main__':
    pattern = "^{}|^{}|^{}|^{}".format('red', 'Red', 'ред', "Ред")
    a = Command_parser('//', pattern)
    print(a.parse('''// py asd test2 test3\nj a\na a'''))
    print(a.parse('''Ред asd asd\ntest2 j'''))
