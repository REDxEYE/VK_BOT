import copy
import traceback
from datetime import *


def CustPrint(*text, type_=None, end=" ", file=None):
    if text[0] == Exception:
        text = [str(text)]
    if text[0] == traceback:
        text = [str(text)]
    if type_ == None:
        type_ = sys._getframe(1).f_code.co_name
    try:
        text = ' '.join([t for t in text])
    except:
        text = str(text)
    template = "[{} {}]: {}\n".format(datetime.now().time(), type_.upper(), text)
    if type == 'err':
        sys.stderr.write(template)
        return
    sys.stdout.write(template)
    return


print_ = copy.deepcopy(__builtins__['print'])

__builtins__['print'] = CustPrint
__builtins__['print_'] = print_
