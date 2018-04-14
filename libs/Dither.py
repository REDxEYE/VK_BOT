from math import floor
from typing import Any

import os.path
from PIL import Image
class Dither:
    size = 800
    fac = 1 #type:Any
    bw = False
    def __init__(self, path):
        self.filename = os.path.basename(path)
        self.filepath = os.path.dirname(path)
        self.im = Image.open(path)  # type: Image.Image
        if self.bw:
            self.im = self.im.convert('L')
        self.resize()


    def resize(self):
        k = self.im.width/self.im.height
        self.im = self.im.resize((int(self.size*k),int(self.size)))

    def find_closest_palette_color(self,color):
        col = []

        if type(color) is list or type(color) is tuple:
            for n,c in enumerate(color):
                if type(self.fac) is tuple or type(self.fac) is list:
                    fac = self.fac[n]
                else:
                    fac = self.fac
                col.append(round(fac * c / 255) * floor(255 / fac)/255)
            return tuple(col)
        else:
            return (round(self.fac * color / 255) * floor(255 / self.fac)/255,)



    @staticmethod
    def dit(col, error, k):
        col = (col / 255) + error * k / 16
        col *=255
        col = int(col)
        return (col,)

    @staticmethod
    def dit_col(col,error,k):
        r = Dither.dit(col[0],error[0],k)[0]
        g = Dither.dit(col[1],error[1],k)[0]
        b = Dither.dit(col[2],error[2],k)[0]

        return (r,g,b,)

    @staticmethod
    def to_float(color):
        if type(color) is list or type(color) is tuple:
            f_color = []
            for c in color:
                f_color.append(c/255)
            return tuple(f_color)
        else:
            return (color/255,)

    @staticmethod
    def sub(col,other_col):
        return tuple([c - o_c for c,o_c in zip(col,other_col)])


    @staticmethod
    def to_int(f_color):
        color = []
        for c in f_color:
            color.append(int(c*255))
        return tuple(color)


    def dither(self):

        for y in range(1, self.im.height - 1):
            for x in range(1, self.im.width - 1):

                old_pixel = self.im.getpixel((x,y))

                new_pixel = self.find_closest_palette_color(old_pixel)

                self.im.putpixel((x,y),self.to_int(new_pixel))

                quant_error = self.sub(self.to_float(old_pixel),new_pixel)
                if self.im.mode == "L":
                    quant_error = quant_error[0]
                    self.im.putpixel((x + 1, y), self.dit(self.im.getpixel((x + 1, y)), quant_error, 7))
                    self.im.putpixel((x - 1, y + 1), self.dit(self.im.getpixel((x - 1, y + 1)), quant_error, 3))
                    self.im.putpixel((x, y + 1), self.dit(self.im.getpixel((x, y + 1)), quant_error, 5))
                    self.im.putpixel((x + 1, y + 1), self.dit(self.im.getpixel((x + 1, y + 1)), quant_error, 1))
                else:
                    self.im.putpixel((x+1,y),self.dit_col(self.im.getpixel((x + 1, y)), quant_error, 7))
                    self.im.putpixel((x-1,y+1),self.dit_col(self.im.getpixel((x - 1, y+1)), quant_error, 3))
                    self.im.putpixel((x,y+1),self.dit_col(self.im.getpixel((x, y+1)), quant_error, 5))
                    self.im.putpixel((x+1,y+1),self.dit_col(self.im.getpixel((x + 1, y+1)), quant_error, 1))




    def save(self):
        self.im.save(os.path.join(self.filepath, self.filename))


if __name__ == '__main__':
    Dither.size = 1000
    Dither.fac = 2
    Dither.bw = False
    a = Dither(r"162_1359226586.vader_san_websizedleopardgeckogirl.jpg")

    a.resize()
    a.dither()
    a.save()
