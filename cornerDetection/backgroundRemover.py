from skimage import color, filters
from scipy import ndimage
import numpy as np


def foregroundMask(im):
    im = np.array(im)
    maxShirtVal = np.max(im)
    shirtImgScaled = im * 255 / maxShirtVal
    grayIm = color.rgb2gray(shirtImgScaled)
    grayIm = filters.apply_hysteresis_threshold(grayIm, 0.15, 0.35)
    sobelEdges = filters.sobel(grayIm)
    filledEdges = np.array(ndimage.binary_fill_holes(sobelEdges), dtype=np.bool)
    if filledEdges[0, 0]:
        filledEdges = np.logical_not(filledEdges)
        # want the top left corner (which denotes background) to be marked as False

    return filledEdges
