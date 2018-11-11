import numpy as np
from skimage.feature import corner_harris, corner_peaks

from cornerDetection.backgroundRemover import foregroundMask

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
    shirt_im = np.array(shirt_im)
    detectedCorners = getAllCorners(shirt_im)
    result = {}
    lowestCornerIndex = 0
    for cornerIndex in range(detectedCorners.shape[0]):
        corner = detectedCorners[cornerIndex]
        if corner[0] > detectedCorners[lowestCornerIndex][0]:
            lowestCornerIndex = cornerIndex
    secondLowestCornerIndex = 1 if (lowestCornerIndex == 0) else 0
    for cornerIndex in range(detectedCorners.shape[0]):
        corner = detectedCorners[cornerIndex]
        if cornerIndex != lowestCornerIndex and corner[0] > detectedCorners[secondLowestCornerIndex][0]:
            secondLowestCornerIndex = cornerIndex
    result['bottomLeftCorner'] = detectedCorners[lowestCornerIndex]
    result['bottomRightCorner'] = detectedCorners[secondLowestCornerIndex]
    if result['bottomRightCorner'][1] < result['bottomLeftCorner'][1]:
        result['bottomRightCorner'], result['bottomLeftCorner'] \
            = result['bottomLeftCorner'], result['bottomRightCorner']
    rightMostCornerIndex = 0
    for cornerIndex in range(detectedCorners.shape[0]):
        corner = detectedCorners[cornerIndex]
        if corner[1] > detectedCorners[rightMostCornerIndex][1]:
            rightMostCornerIndex = cornerIndex
    result['rightSleeveTopCorner'] = detectedCorners[rightMostCornerIndex]
    leftMostCornerIndex = 0
    for cornerIndex in range(detectedCorners.shape[0]):
        corner = detectedCorners[cornerIndex]
        if corner[1] < detectedCorners[leftMostCornerIndex][1]:
            leftMostCornerIndex = cornerIndex
    result['leftSleeveTopCorner'] = detectedCorners[leftMostCornerIndex]
    midLevelCorners = []
    pointSeparationDelta0 = shirt_im.shape[0] / 100
    for cornerIndex in range(detectedCorners.shape[0]):
        corner = detectedCorners[cornerIndex]
        if result['leftSleeveTopCorner'][0] + pointSeparationDelta0 < \
                corner[0] < result['bottomLeftCorner'][0] - pointSeparationDelta0:
            midLevelCorners.append(corner)
    midLevelCorners = sorted(midLevelCorners, key=lambda x: x[1])
    if len(midLevelCorners) > 0:
        leftMidCorner = midLevelCorners[0]
        rightMidCorner = midLevelCorners[len(midLevelCorners) - 1]
        result['leftSleeveBottomCorner'] = leftMidCorner
        result['rightSleeveBottomCorner'] = rightMidCorner
        midPointXVal = (result['leftSleeveBottomCorner'][1] - result['rightSleeveBottomCorner'][1]) / 2
    return result
