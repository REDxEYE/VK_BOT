import urllib
import urllib.request
from urllib.request import urlopen

import ConsoleLogger
from DataTypes.LongPoolHistoryUpdate import LongPoolHistoryMessage, Updates
from DataTypes.attachments import attachment
from Module_manager_v2 import ModuleManager

from libs import Dither
from libs.tempfile_ import TempFile
from modules.__Command_template import C_template

LOGGER = ConsoleLogger.ConsoleLogger('PIL_COMMANDS')

HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

@ModuleManager.command(names=["дизер"], perm='photo.dither', desc="Дизерит фото")
@ModuleManager.argument('depth',1,'Глубина цвета',False)
@ModuleManager.argument('bw',0,r'Ч\Б?',False)
class Ditherer(C_template):

    def __call__(self, data: LongPoolHistoryMessage, LongPoolUpdates: Updates, ):
        atts = data.attachments
        photo = atts[0].photo.GetHiRes
        req = urllib.request.Request(photo, headers=HDR)
        img = urlopen(req).read()
        Tmp = TempFile(img, 'jpg')
        data.send_back("А теперь подождите, штука эта не быстрая",fwd=False)
        print("ДИЗЕР",self.vars.depth,self.vars.bw)
        Dither.Dither.fac = self.vars.depth
        Dither.Dither.bw = bool(self.vars.bw)
        dit = Dither.Dither(Tmp.path_)
        # dit.resize()
        dit.dither()
        dit.save()
        att = self.api.UploadFromDisk(Tmp.path_)
        Tmp.rem()

        data.send_back(":D", att, True)
        return True

