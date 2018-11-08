import numpy as np
from skimage.feature import corner_harris, corner_peaks
from backgroundRemover import foregroundMask

k = 0.05


def getAllCorners(im):
    im = np.array(foregroundMask(im))
    harris_corner_response_image = None
    if k is None:
        harris_corner_response_image = corner_harris(im)
    else:
        harris_corner_response_image = corner_harris(im, k=k)
    return corner_peaks(harris_corner_response_image, min_distance=1)


def getShirtCorners(shirt_im):
    detectedCorners = getAllCorners(shirt_im)
    # TODO: Implement
    result = {}
    return result
