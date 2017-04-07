import math
import os.path
import random

import cv2
import imageio
import numpy as np
from PIL import Image, ImageSequence, ImageChops, ImageFont, ImageDraw, ImageEnhance

from libs.tempfile_ import TempFile


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

        for i in range(1, random.randint(3, 6)):
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


def extendgif(gif, lenT):
    print('list gif len: ', len(gif))
    gifB = gif
    while len(gif) < lenT:
        gif += gifB
    print('returning gif len: ', len(gif))
    return gif


def MakeGlitchGifVSH(image, len_=60, blockSize=16, sigma=10, iterations=300, random_=True, Glitch_=False):
    im = Image.open(image)
    VSH = imageio.mimread(os.path.join('IMAGES','vsh.gif'))
    VSH = extendgif(VSH, len_)
    nFrames = []

    glitchVar = 0

    path = '/'.join(image.split('/')[:-1])
    pathT = '/'.join(image.split('/')[:-1])
    name = image.split('/')[-1]
    fname = name.split('.')[0]
    path += '/glitch_' + fname + '.gif'

    frames = [im.copy() for a in range(len_)]
    i = 0
    for frame in frames:
        i += 1

        if random.randint(0, 15) >= 10 and glitchVar == 0:
            glitchVar = random.randint(1, sigma)
        if glitchVar != 0:
            frame = GlitchRet(frame.convert('RGB'), Glitch_=Glitch_, sigma=glitchVar, blockSize=blockSize,
                              iterations=iterations, random_=random_)
            glitchVar -= 1
        frame = ImageChops.multiply(frame, Image.fromarray(VSH[i]).resize(frame.size).convert('RGB'))
        nFrames.append(np.asarray(frame.convert('RGB')))
    i = 0
    imageio.mimwrite(path, nFrames, )

    return path


def GlitchGif(gif, blockSize=16, sigma=10, iterations=300, random_=True, Glitch_=False):
    im = Image.open(gif)
    nFrames = []
    glitchVar = 0
    # original_duration = im.info['duration']
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
    # fps = (original_duration) / 1000
    # print(fps)
    # imageio.mimwrite(path, nFrames, **{'duration': fps})
    imageio.mimwrite(path, nFrames, )
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


def roll(imageF, delta):
    im = Image.open(imageF)

    xsize, ysize = im.size

    if delta > xsize:
        delta = xsize - 5
    if delta > ysize:
        delta -= ysize
    print(delta)
    for i in range(0, ysize - 1):
        part1 = im.crop((0, i, delta + i, i + 1))
        part2 = im.crop((delta + i, i, xsize, i + 1))
        part1.load()
        part2.load()
        im.paste(part2, (0, i, xsize - (delta + i), i + 1))
        im.paste(part1, (xsize - (delta + i), i, xsize, i + 1))
    im.save(imageF)


def rollRandom(imageF):
    im = Image.open(imageF)

    xsize, ysize = im.size

    if random.randrange(-5, 2, 1) >= 0:
        for i in range(0, ysize - 1):
            yr = round(random.randint(0, ysize - 10) / 10)
            if random.randrange(-5, 2, 1) >= 0:
                part1 = im.crop((0, i, yr, i + 1))
                part2 = im.crop((yr, i, xsize, i + 1))
                part1.load()
                part2.load()
                im.paste(part2, (0, i, xsize - yr, i + 1))
                im.paste(part1, (xsize - yr, i, xsize, i + 1))
            else:
                part1 = im.crop((0, i, yr, i + 1))
                part2 = im.crop((yr, i, xsize, i + 1))

                part1.load()
                part2.load()
                im.paste(part1, (xsize - yr, i, xsize, i + 1))
                im.paste(part2, (0, i, xsize - yr, i + 1))

    im.save(imageF)


def rollsmast(imageF):
    im = Image.open(imageF)

    xsize, ysize = im.size

    for i in range(0, ysize - 1):
        yr = 0
        if random.randint(0, 15) >= 10 and yr == 0:
            yr = round(random.randint(0, ysize - 10) / 10)

        if yr != 0:
            if random.randrange(-5, 2, 1) >= 0:
                part1 = im.crop((0, i, yr, i + 1))
                part2 = im.crop((yr, i, xsize, i + 1))
                part1.load()
                part2.load()
                im.paste(part2, (0, i, xsize - yr, i + 1))
                im.paste(part1, (xsize - yr, i, xsize, i + 1))
            else:
                part1 = im.crop((0, i, yr, i + 1))
                part2 = im.crop((yr, i, xsize, i + 1))

                part1.load()
                part2.load()
                im.paste(part1, (xsize - yr, i, xsize, i + 1))
                im.paste(part2, (0, i, xsize - yr, i + 1))
    im.save(imageF)


def Transorm(orig, im, origshape):
    height, width, channels = im.shape
    dest_pts = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    M = cv2.getPerspectiveTransform(dest_pts, orig)
    drawing = cv2.warpPerspective(im, M, origshape)
    return drawing


def Wanted(im1, im2):
    wanted = cv2.imread(os.path.join('IMAGES','Wanted.JPG'))
    toplace1 = cv2.flip(cv2.imread(im1), 1)
    toplace2 = cv2.flip(cv2.imread(im2), 1)
    height2, width2, channels2 = wanted.shape
    orig_pts = np.float32([[592, 265], [397, 241], [550, 535],
                           [350, 500]])
    orig_pts2 = np.float32([[800, 312], [608, 277], [755, 570],
                            [560, 535]])
    images = [toplace1, toplace2]
    transforms = [orig_pts, orig_pts2]
    out = []
    for transform, image in zip(transforms, images):
        drawing = Transorm(transform, image, (width2, height2))
        out.append(drawing)
    toplace = np.array(ImageChops.screen(Image.fromarray(cv2.cvtColor(out[0], cv2.COLOR_BGR2RGB)),
                                         Image.fromarray(cv2.cvtColor(out[1], cv2.COLOR_BGR2RGB))))
    wante = np.array(
        ImageChops.screen(Image.fromarray(wanted), Image.fromarray(cv2.cvtColor(toplace, cv2.COLOR_BGR2RGB))))
    final = Image.fromarray((cv2.cvtColor(wante, cv2.COLOR_BGR2RGB)))
    final.save(im1)


def textPlain(text, size, font='times.ttf', x=100, y=200, xsize=1280, ysize=720):
    im = Image.new('RGB', (xsize, ysize), color=(255, 255, 255))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(font, int(size))
    draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))
    _path = TempFile.generatePath('png')
    im.save(_path)
    return _path


def JonTron(im1):
    JonTron = Image.open(os.path.join('IMAGES','JonTron.png'))
    toplace = cv2.flip(cv2.imread(im1), 1)
    width2, height2 = JonTron.size
    orig_pts = np.float32([[840, 238], [581, 233],
                           [805, 515], [535, 478]])
    drawing = Transorm(orig_pts, toplace, (width2, height2))
    final = Image.fromarray(cv2.cvtColor(drawing, cv2.COLOR_BGR2RGB))
    final.paste(JonTron, (0, 0), JonTron)
    final.save(im1)


def SayMax(im1):
    JonTron = Image.open(os.path.join('IMAGES','SayMax.png'))
    toplace = cv2.flip(cv2.imread(im1), 1)
    width2, height2 = JonTron.size
    orig_pts = np.float32([[353, 243], [0, 280],
                           [352, 473], [26, 493]])
    drawing = Transorm(orig_pts, toplace, (width2, height2))
    final = Image.fromarray(cv2.cvtColor(drawing, cv2.COLOR_BGR2RGB))
    final.paste(JonTron, (0, 0), JonTron)
    final.save(im1)


def resize_(x, imf, sharp=False, ret=False):
    if ret:
        im = imf
    else:
        im = Image.open(imf)
    ox, oy = im.size
    y = round((x / ox) * oy)
    im = im.resize((x, y), Image.LANCZOS)
    if sharp:
        enhancer = ImageEnhance.Sharpness(im)
        im = enhancer.enhance(2)
    if ret:
        return im
    else:
        im.save(imf)
