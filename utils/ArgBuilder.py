from DataTypes.attachments import attachment


class Args_def:
    def __init__(self):
        self.v = '5.60'


class Args_message(Args_def):
    def __init__(self):
        super(Args_message, self).__init__()
        self.peer_id = None
        self.message = ''
        self.attachment = []
        self.forward_messages = []  # type: list[int]

    def AddAttachment(self, *attachments: attachment):
        template = '{}{}_{}'
        template_AccessKey = '{}{}_{}_{}'
        for att in attachments:
            Owner,Id,accesskey = att.GetOwnerAndId(att.type)
            if accesskey != None:
                temp = template_AccessKey.format(att.type, Owner, Id, accesskey)
            else:
                temp = template.format(att.type, Owner, Id)
            self.attachment.append(temp)

    def AsDict_(self) -> dict:
        return {var: vars(self)[var] for var in vars(self) if vars(self)[var] != None}


if __name__ == "__main__":
    a = Args_message()
    print(a.AsDict_())
