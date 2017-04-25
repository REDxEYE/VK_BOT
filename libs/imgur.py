from typing import List, Union

import imgurpython

from imgurpython import ImgurClient
from imgurpython.imgur.models.gallery_album import GalleryAlbum
from imgurpython.imgur.models.gallery_image import GalleryImage
client_id = '74b33fb389fc3f4'
client_secret = '14bfd5491fe9731372c2f3e857a5820df5148414'


class Imgur:

    def __init__(self):
        self.client = ImgurClient(client_id, client_secret)

    def get(self,q):
        alb = self.client.gallery_search(q= q)
        return [self.client.get_image(a.id).link for a in alb if isinstance(a,GalleryImage)]
