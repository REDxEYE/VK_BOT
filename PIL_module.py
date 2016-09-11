import math
import random

from PIL import Image


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


def Glitch(file, blockSize=16, sigma=0.01, iterations=300, random_=True):
    im = Image.open(file)
    a = WigglyBlocks(blockSize, sigma, iterations, random_)
    im = a.render(im)
    im.save(file, 'JPEG')
