import os.path
import random
from multiprocessing.pool import ThreadPool
try:
    import cv2

    cv2Avalible = True
except:
    cv2 = None
    cv2Avalible = False
import numpy as np
from PIL import Image, ImageOps, ImageChops

try:
    from scipy.interpolate import UnivariateSpline
    scipyAvalible = True
except:
    scipyAvalible = False
    UnivariateSpline = None
xrange = range

try:
    from .__Command_template import *
except:
    from __Command_template import *

from Module_manager_v2 import ModuleManager

@ModuleManager.Filter(name= 'PencilSketch',desc="Карандашный набросок")
class Filter_PencilSketch(F_template):
    enabled = cv2Avalible
    name = 'PencilSketch'
    desc = "Карандашный набросок"
    """Pencil sketch effect

        A class that applies a pencil sketch effect to an image.
        The processed image is overlayed over a background image for visual
        effect.
    """

    def __init__(self, bg_gray='pencilsketch_bg.jpg'):
        """Initialize parameters

            :param (width, height): Image size.
            :param bg_gray: Optional background image to improve the illusion
                            that the pencil sketch was drawn on a canvas.
        """

        self.bg = os.path.join('IMAGES',bg_gray)

    def render(self, img_rgb):
        """Applies pencil sketch effect to an RGB image

            :param img_rgb: RGB image to be processed
            :returns: Processed RGB image
        """
        path = img_rgb
        img_rgb = cv2.imread(img_rgb)
        w, h, _ = img_rgb.shape
        print(w, h)
        self.canvas = cv2.imread(self.bg, cv2.CV_8UC1)
        if self.canvas is not None:
            self.canvas = cv2.resize(self.canvas, (h, w))

        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (21, 21), 0, 0)
        img_blend = cv2.divide(img_gray, img_blur, scale=256)

        # if available, blend with background canvas
        if self.canvas is not None:
            img_blend = cv2.multiply(img_blend, self.canvas, scale=1. / 256)
        img_blend = cv2.cvtColor(img_blend, cv2.COLOR_GRAY2RGB)
        cv2.imwrite(path, img_blend)
        # return

@ModuleManager.Filter(name= 'Cartoonizer',desc="Мультфильм фильтр")
class Filter_Cartoonizer(F_template):
    enabled = cv2Avalible
    name = 'Cartoonizer'
    desc = "Мультфильм фильтр"
    """Cartoonizer effect

        A class that applies a cartoon effect to an image.
        The class uses a bilateral filter and adaptive thresholding to create
        a cartoon effect.
    """

    def __init__(self):
        pass

    def render(self, img_rgb):
        numDownSamples = 2  # number of downscaling steps
        numBilateralFilters = 7  # number of bilateral filtering steps
        path = img_rgb
        img_rgb = cv2.imread(img_rgb)
        # -- STEP 1 --
        # downsample image using Gaussian pyramid
        img_color = img_rgb
        for _ in xrange(numDownSamples):
            img_color = cv2.pyrDown(img_color)

        # repeatedly apply small bilateral filter instead of applying
        # one large filter
        for _ in xrange(numBilateralFilters):
            img_color = cv2.bilateralFilter(img_color, 9, 9, 7)

        # upsample image to original size
        for _ in xrange(numDownSamples):
            img_color = cv2.pyrUp(img_color)

        # -- STEPS 2 and 3 --
        # convert to grayscale and apply median blur
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        img_blur = cv2.medianBlur(img_gray, 7)

        # -- STEP 4 --
        # detect and enhance edges
        img_edge = cv2.adaptiveThreshold(img_blur, 255,
                                         cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY, 9, 2)

        # -- STEP 5 --
        # convert back to color so that it can be bit-ANDed with color image
        w, h, _ = img_rgb.shape

        img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
        img_edge = cv2.resize(img_edge, (h, w))
        cv2.imwrite(path, cv2.bitwise_and(img_color, img_edge))
        # return cv2.bitwise_and(img_color, img_edge)

@ModuleManager.Filter(name= 'Equal',desc="Уравнивающий фильтр")
class Filter_Equal(F_template):
    name = 'Equal'
    desc = "Уравнивающий фильтр"

    def __init__(self):
        pass

    def render(self, img):
        im = Image.open(img)
        im = ImageOps.equalize(im)
        im.save(img, 'PNG')

@ModuleManager.Filter(name= 'AutoContrast',desc='Автоконтраст')
class Filter_AutoContrast(F_template):
    name = 'AutoContrast'
    desc = "Автоконтраст"

    def __init__(self):
        pass

    def render(self, img):
        im = Image.open(img)
        im = ImageOps.autocontrast(im, 5)
        im.save(img, 'PNG')

@ModuleManager.Filter(name= 'Tlen',desc="Тлен")
class Filter_Tlen(F_template):
    name = 'Tlen'
    desc = "Тлен"

    def __init__(self):
        pass

    def render(self, img):
        im = Image.open(img).convert('L').convert('RGB')
        im2 = Image.open(random.choice([os.path.join('IMAGES','tlen.jpeg'), os.path.join('IMAGES','tlen2.jpg'), os.path.join('IMAGES','tlen3.jpg')])).resize(im.size).convert('RGB')
        im = ImageChops.multiply(im, im2)
        im.save(img, 'JPEG')

@ModuleManager.Filter(name= 'Neural',desc="Нейронный фильтр")
class Filter_Neural(F_template):
    enabled = cv2Avalible
    name = 'Neural'
    desc = "Нейронный фильтр"

    def __init__(self):
        pass

    def render(self, im, ret=False, inp=False):
        if inp:
            img = np.array(im)
        else:
            img = cv2.imread(im)
        if img.shape[0] < 2000:
            w = img.shape[1]
            h = img.shape[0]
            k = 2000 / w

            img = cv2.resize(img, (2000, int(h * k)))

        filters = self.build_filters()
        res2 = self.process_threaded(img, filters)
        if ret:
            return res2
        else:
            cv2.imwrite(im, res2)

    def build_filters(self):
        filters = []

        ksize = 150
        for theta in np.arange(0, np.pi, np.pi / 16):
            kern = cv2.getGaborKernel((ksize, ksize), 4.0, theta, 10.0, 0.7, 0, ktype=cv2.CV_32F)
            kern /= 1.5 * kern.sum()
            filters.append(kern)

        return filters

    def process_threaded(self, img, filters, threadn=8):
        accum = np.zeros_like(img)

        def f(kern):
            return cv2.filter2D(img, cv2.CV_8UC3, kern)

        pool = ThreadPool(processes=threadn)
        for fimg in pool.imap_unordered(f, filters):
            np.maximum(accum, fimg, accum)
        return accum

@ModuleManager.Filter(name= 'Neural2',desc="Нейронный фильтр Sigma 6")
class Filter_Neural2(F_template):
    enabled = cv2Avalible
    name = 'Neural2'
    desc = "Нейронный фильтр Sigma 6"

    def __init__(self):
        pass

    def render(self, im, ret=False, inp=False):
        if inp:
            img = np.array(im)
        else:
            img = cv2.imread(im)
        if img.shape[0] < 2000:
            w = img.shape[1]
            h = img.shape[0]
            k = 2000 / w

            img = cv2.resize(img, (2000, int(h * k)))
        filters = self.build_filters()
        res2 = self.process_threaded(img, filters)
        if ret:
            return res2
        else:
            cv2.imwrite(im, res2)

    def build_filters(self):
        filters = []

        ksize = 150
        for theta in np.arange(0, np.pi, np.pi / 16):
            kern = cv2.getGaborKernel((ksize, ksize), 6.0, theta, 10.0, 0.7, 0, ktype=cv2.CV_32F)
            kern /= 1.5 * kern.sum()
            filters.append(kern)

        return filters

    def process_threaded(self, img, filters, threadn=8):
        accum = np.zeros_like(img)

        def f(kern):
            return cv2.filter2D(img, cv2.CV_8UC3, kern)

        pool = ThreadPool(processes=threadn)
        for fimg in pool.imap_unordered(f, filters):
            np.maximum(accum, fimg, accum)
        return accum

@ModuleManager.Filter(name= 'Neural3',desc="Нейронный фильтр Sigma 5")
class Filter_Neural3(F_template):
    enabled = cv2Avalible
    name = 'Neural3'
    desc = "Нейронный фильтр sigma 5"

    def __init__(self):
        pass

    def render(self, im, ret=False, inp=False):
        if inp:
            img = np.array(im)
        else:
            img = cv2.imread(im)
        if img.shape[0] < 2000:
            w = img.shape[1]
            h = img.shape[0]
            k = 2000 / w

            img = cv2.resize(img, (2000, int(h * k)))
        filters = self.build_filters()
        res2 = self.process_threaded(img, filters)
        if ret:
            return res2
        else:
            cv2.imwrite(im, res2)

    def build_filters(self):
        filters = []

        ksize = 150
        for theta in np.arange(0, np.pi, np.pi / 16):
            kern = cv2.getGaborKernel((ksize, ksize), 5.0, theta, 10.0, 0.7, 0, ktype=cv2.CV_32F)
            kern /= 1.5 * kern.sum()
            filters.append(kern)

        return filters

    def process_threaded(self, img, filters, threadn=8):
        accum = np.zeros_like(img)

        def f(kern):
            return cv2.filter2D(img, cv2.CV_8UC3, kern)

        pool = ThreadPool(processes=threadn)
        for fimg in pool.imap_unordered(f, filters):
            np.maximum(accum, fimg, accum)
        return accum

@ModuleManager.Filter(name= 'Neural_Edges',desc="Нейронный фильтр глубокий")
class Filter_Neural_Edges(F_template):
    enabled = cv2Avalible
    name = 'Neural_Edges'
    desc = "Нейронный фильтр глубокий"

    def __init__(self):
        pass

    def render(self, im, ret=False, inp=False):
        if inp:
            img = np.array(im)
        else:
            img = cv2.imread(im)
        if img.shape[0] < 2000:
            w = img.shape[1]
            h = img.shape[0]
            k = 2000 / w

            img = cv2.resize(img, (2000, int(h * k)))
        filters = self.build_filters()
        res2 = self.process_threaded(img, filters)
        if ret:
            return res2
        else:
            cv2.imwrite(im, res2)


    def build_filters(self):
        filters = []

        ksize = 150
        for theta in np.arange(0, np.pi, np.pi / 16):
            kern = cv2.getGaborKernel((ksize, ksize), 4.0, theta, 10.0, 0.7, 0.5, ktype=cv2.CV_32F)
            kern /= 1.5 * kern.sum()
            filters.append(kern)

        return filters

    def process_threaded(self, img, filters, threadn=8):
        accum = np.zeros_like(img)

        def f(kern):
            return cv2.filter2D(img, cv2.CV_8UC3, kern)

        pool = ThreadPool(processes=threadn)
        for fimg in pool.imap_unordered(f, filters):
            np.maximum(accum, fimg, accum)
        return accum

@ModuleManager.Filter(name= 'Neural_Edges2',desc="Нейронный фильтр глубокий 2")
class Filter_Neural_Edges2(F_template):
    enabled = cv2Avalible
    name = 'Neural_Edges2'
    desc = "Нейронный фильтр глубокий 2"

    def __init__(self):
        pass

    def render(self, im, ret=False, inp=False):
        if inp:
            img = np.array(im)
        else:
            img = cv2.imread(im)
        if img.shape[0] < 2000:
            w = img.shape[1]
            h = img.shape[0]
            k = 2000 / w

            img = cv2.resize(img, (2000, int(h * k)))
        filters = self.build_filters()
        res2 = self.process_threaded(img, filters)
        if ret:
            return res2
        else:
            cv2.imwrite(im, res2)

    def build_filters(self):
        filters = []

        ksize = 150
        for theta in np.arange(0, np.pi, np.pi / 16):
            kern = cv2.getGaborKernel((ksize, ksize), 4.0, theta, 10.0, 0.7, 5, ktype=cv2.CV_32F)
            kern /= 2 * kern.sum()
            filters.append(kern)

        return filters

    def process_threaded(self, img, filters, threadn=8):
        accum = np.zeros_like(img)

        def f(kern):
            return cv2.filter2D(img, cv2.CV_8UC3, kern)

        pool = ThreadPool(processes=threadn)
        for fimg in pool.imap_unordered(f, filters):
            np.maximum(accum, fimg, accum)
        return accum
