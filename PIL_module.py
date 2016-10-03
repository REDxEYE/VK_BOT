import math
import random

import imageio
import numpy as np
from PIL import Image, ImageSequence, ImageChops


def kok(file):
    im = Image.open(file)
    xsize, ysize = im.size
    ysize2 = int(ysize / 2)
    xsize2 = int(xsize / 2)

    im2 = im.transpose(Image.FLIP_LEFT_RIGHT)
    part1 = im2.crop((0, 0, xsize2, ysize))
    part2 = im.crop((xsize2, 0, xsize, ysize))
    part1.load()
    part2.load()
    im.paste(part1, (0, 0, xsize2, ysize))
    im.paste(part2, (xsize2, 0, xsize, ysize))
    im.save(file, 'JPEG')


def kek(file):
    im = Image.open(file)
    xsize, ysize = im.size
    ysize2 = int(ysize / 2)
    xsize2 = int(xsize / 2)

    im2 = im.transpose(Image.FLIP_LEFT_RIGHT)
    part1 = im.crop((0, 0, xsize2, ysize))
    part2 = im2.crop((xsize2, 0, xsize, ysize))
    part1.load()
    part2.load()
    im.paste(part1, (0, 0, xsize2, ysize))
    im.paste(part2, (xsize2, 0, xsize, ysize))
    im.save(file, 'JPEG')


class WigglyBlocks():
    """Randomly select and shift blocks of the image"""

    def __init__(self, blockSize=16, sigma=0.01, iterations=300, random_=True):
        self.blockSize = blockSize
        self.blockSizex = self.blockSize + random.randint(-blockSize, blockSize)
        self.blockSizey = self.blockSize + random.randint(-blockSize, blockSize)
        self.sigma = sigma
        self.random_ = random_
        self.iterations = iterations
        self.seed = random.random()

    def render(self, image):
        r = random.Random(self.seed)
        for i in range(self.iterations):
            if self.random_:
                self.blockSizex = self.blockSize + random.randint(-self.blockSize, self.blockSize)
                self.blockSizey = self.blockSize + random.randint(-self.blockSize, self.blockSize)
            # Select a block
            bx = int(r.uniform(0, image.size[0] - self.blockSizex))
            by = int(r.uniform(0, image.size[1] - self.blockSizey))
            block = image.crop((bx, by, bx + self.blockSizex - 1, by + self.blockSizey - 1))

            # Figure out how much to move it.
            # The call to floor() is important so we always round toward
            # 0 rather than to -inf. Just int() would bias the block motion.
            mx = int(math.floor(r.normalvariate(0, self.sigma)))
            my = int(math.floor(r.normalvariate(0, self.sigma)))

            # Now actually move the block
            image.paste(block, (bx + mx, by + my))
        return image


class Glitch2():
    @staticmethod
    def get_random_start_and_end_points_in_file(file_data):
        start_point = random.randint(0, len(file_data))
        end_point = start_point + random.randint(0, len(file_data) - start_point)

        return start_point, end_point

    @staticmethod
    def splice_a_chunk_in_a_file(file_data):
        start_point, end_point = Glitch2.get_random_start_and_end_points_in_file(file_data)
        section = file_data[start_point:end_point]
        repeated = b''

        for i in range(1, random.randint(1, 10)):
            repeated += section

        new_start_point, new_end_point = Glitch2.get_random_start_and_end_points_in_file(file_data)
        file_data = file_data[:new_start_point] + repeated + file_data[new_end_point:]
        return file_data

    @staticmethod
    def glitch_an_image(local_image):
        file_handler = open(local_image, 'r+b')
        file_data = file_handler.read()
        file_handler.close()

        for i in range(1, random.randint(3, 13)):
            file_data = Glitch2.splice_a_chunk_in_a_file(file_data)

        file_handler = open(local_image, 'w+b')
        file_handler.write(file_data)
        file_handler.close

        return local_image


def GlitchRet(im, blockSize=16, sigma=5, iterations=300, random_=True, Glitch_=False):
    # im = Image.open(file)
    im = im.convert('RGB')
    a = WigglyBlocks(blockSize, sigma, iterations, random_)
    if Glitch_:
        R = Image.new("RGB", im.size)
        G = Image.new("RGB", im.size)
        B = Image.new("RGB", im.size)

        R.putdata(im.getdata(0))
        G.putdata(im.getdata(1))
        B.putdata(im.getdata(2))
        R = a.render(R).convert('L')
        G = a.render(G).convert('L')
        B = a.render(B).convert('L')

        im = Image.merge('RGB', (R, G, B))
        im = im.point(lambda p: p * 3.5)
    else:

        im = a.render(im)
    # im.save(file, 'JPEG')
    return im


def Glitch(file, blockSize=16, sigma=0.01, iterations=300, random_=True, Glitch_=False):
    im = Image.open(file)
    a = WigglyBlocks(blockSize, sigma, iterations, random_)
    if Glitch_:
        R = Image.new("RGB", im.size)
        G = Image.new("RGB", im.size)
        B = Image.new("RGB", im.size)

        R.putdata(im.getdata(0))
        G.putdata(im.getdata(1))
        B.putdata(im.getdata(2))
        R = a.render(R).convert('L')
        G = a.render(G).convert('L')
        B = a.render(B).convert('L')

        im = Image.merge('RGB', (R, G, B))
        im = im.point(lambda p: p * 3.5)
    else:

        im = a.render(im)
    im.save(file, 'JPEG')


def MakeGlitchGif(image, len_=60, blockSize=16, sigma=10, iterations=300, random_=True, Glitch_=False):
    im = Image.open(image)
    nFrames = []
    glitchVar = 0

    path = '/'.join(image.split('/')[:-1])
    name = image.split('/')[-1]
    fname = name.split('.')[0]
    path += '/glitch_' + fname + '.gif'

    frames = [im.copy() for a in range(len_)]
    for frame in frames:

        if random.randint(0, 15) >= 10 and glitchVar == 0:
            glitchVar = random.randint(1, sigma)
        if glitchVar != 0:
            frame = GlitchRet(frame.convert('RGB'), Glitch_=True, sigma=glitchVar, blockSize=blockSize,
                              iterations=iterations, random_=random_)
            glitchVar -= 1
        nFrames.append(np.asarray(frame.convert('RGB')))

    imageio.mimwrite(path, nFrames, )
    return path


def GlitchGif(gif, blockSize=16, sigma=10, iterations=300, random_=True, Glitch_=False):
    im = Image.open(gif)
    nFrames = []
    glitchVar = 0
    original_duration = im.info['duration']
    path = '/'.join(gif.split('/')[:-1])
    name = gif.split('/')[-1]
    path += '/glitch_' + name
    print(path)
    for frame in ImageSequence.Iterator(im):
        if random.randint(0, 15) >= 10 and glitchVar == 0:
            glitchVar = random.randint(1, sigma)
        if glitchVar != 0:
            frame = GlitchRet(frame.convert('RGB'), Glitch_=True, sigma=glitchVar, blockSize=blockSize,
                              iterations=iterations, random_=random_)
            glitchVar -= 1
        nFrames.append(np.asarray(frame.convert('RGB')))
    fps = (original_duration) / 1000
    print(fps)
    imageio.mimwrite(path, nFrames, **{'duration': fps})
    return path


def add(im1F, im2F):
    path1 = '/'.join(im1F.split('/')[:-1])
    name1 = im1F.split('/')[-1]
    fname1 = name1.split('.')[0]
    name2 = im2F.split('/')[-1]
    fname2 = name2.split('.')[0]
    im1 = Image.open(im1F)
    im2 = Image.open(im2F)
    im2 = im2.resize(im1.size)
    im3 = ImageChops.add(im1, im2)
    im3.save(im1F)
