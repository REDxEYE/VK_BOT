import copy
import sys
import traceback
from datetime import *


def CustPrint(*text, type_=None, end=" ", file=None):
    if text[0] == Exception:
        text = [str(text)]
    if text[0] == traceback:
        text = [str(text)]
    if type_ == None:
        type_ = sys._getframe(1).f_code.co_name
    a = []
    for t in text:

        if isinstance(t, tuple):
            t = list(t)
        else:
            t = t
        a.append(t)

    try:
        text = ' '.join(list([str(t) for t in a]))
    except:
        text = str(text)

    template = "[{} {}]: {}\n".format(str(datetime.now().time())[:-3], type_.upper(), text)
    if type == 'err':
        sys.stderr.write(template)
        return
    sys.stdout.write(template)
    return


print_ = copy.deepcopy(__builtins__['print'])
__builtins__['print'] = CustPrint
__builtins__['print_'] = print_
print('custom print loaded')
