import numpy as np
from skimage.feature import corner_harris, corner_peaks
from skimage import color, filters
from scipy import ndimage
# from backgroundRemover import foregroundMask

k = 0.05

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

def foregroundMaskWithoutCollar(imMask, shirtCorners):
    # imMask should be the original mask used to find the shirt corners
    # shirtCorners should be the dictionary of points
    leftNeckCorner = shirtCorners['leftNeckCorner']
    rightNeckCorner = shirtCorners['rightNeckCorner']
    collarCenterX = (rightNeckCorner[0] - leftNeckCorner[0]) // 2 + leftNeckCorner[0]
    collarCenterY = (rightNeckCorner[1] - leftNeckCorner[1]) // 2 + leftNeckCorner[1]
    leftShoulder = shirtCorners['leftShoulderCorner']
    rightShoulder = shirtCorners['rightShoulderCorner']
    avgShouldHeight = (rightShoulder[1] - leftShoulder[1]) // 2 + leftShoulder[1]

    radius = (rightNeckCorner[0] - leftNeckCorner[0]) // 2
    imMaskCopy = imMask.copy()

    for y, row in enumerate(imMask):
        for x, col in enumerate(row):
            # if y > avgShouldHeight:
            #     break # no need to check below shoulder height
            if col:
                # if the current spot is marked True, check if it should be False
                if (y - collarCenterY)**2 + (x - collarCenterX)**2 <= radius**2:
                    imMaskCopy[y][x] = False

    return imMaskCopy

def getAllCorners(im):
    foreground_mask_im = np.array(foregroundMask(im))
    harris_corner_response_image = None
    if k is None:
        harris_corner_response_image = corner_harris(foreground_mask_im)
    else:
        harris_corner_response_image = corner_harris(foreground_mask_im, k=k)
    return corner_peaks(harris_corner_response_image, min_distance=1)


def getShirtCorners(shirt_im):
    shirt_im = np.array(shirt_im)
    foreground_mask_im = np.array(foregroundMask(shirt_im))
    detectedCorners = getAllCorners(foreground_mask_im)
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
    pointSeparationDelta0 = shirt_im.shape[0] / 20
    pointSeparationDelta1 = shirt_im.shape[1] / 20
    for cornerIndex in range(detectedCorners.shape[0]):
        corner = detectedCorners[cornerIndex]
        if result['leftSleeveTopCorner'][0] < corner[0] < result['bottomLeftCorner'][0] - pointSeparationDelta0\
                and result['leftSleeveTopCorner'][1] + pointSeparationDelta1 < corner[1] < result['rightSleeveTopCorner'][1] - pointSeparationDelta1:
            midLevelCorners.append(corner)
    midLevelCorners = sorted(midLevelCorners, key=lambda x: x[1])
    if len(midLevelCorners) > 0:
        leftMidCorner = midLevelCorners[0]
        rightMidCorner = midLevelCorners[len(midLevelCorners) - 1]
        result['leftSleeveBottomCorner'] = leftMidCorner
        result['rightSleeveBottomCorner'] = rightMidCorner
    leftShoulderCorner = np.array([shirt_im.shape[0] - 1, shirt_im.shape[1] - 1], dtype=np.int64)
    rightShoulderCorner = np.array([shirt_im.shape[0] - 1, 0], dtype=np.int64)

    shoulderXMult = 1
    shoulderYMult = -1.3
    for y in range(shirt_im.shape[0]):
        for x in range(shirt_im.shape[1]):
            if foreground_mask_im[y, x]:
                if -1 * shoulderXMult * x + shoulderYMult * y > -1 * shoulderXMult * leftShoulderCorner[1] + shoulderYMult * leftShoulderCorner[0]:
                    leftShoulderCorner[1] = x
                    leftShoulderCorner[0] = y
                if shoulderXMult * x + shoulderYMult * y > shoulderXMult * rightShoulderCorner[1] + shoulderYMult * rightShoulderCorner[0]:
                    rightShoulderCorner[1] = x
                    rightShoulderCorner[0] = y
    result['leftShoulderCorner'] = leftShoulderCorner
    result['rightShoulderCorner'] = rightShoulderCorner

    leftNeckCorner = np.array([shirt_im.shape[0] - 1, shirt_im.shape[1] - 1], dtype=np.int64)
    rightNeckCorner = np.array([shirt_im.shape[0] - 1, 0], dtype=np.int64)
    for y in range(shirt_im.shape[0]):
        for x in range(shirt_im.shape[1]):
            if foreground_mask_im[y, x]:
                if abs(x - result['leftShoulderCorner'][1]) < abs(x - result['rightShoulderCorner'][1]) \
                        and leftNeckCorner[0] > y:
                    leftNeckCorner[1] = x
                    leftNeckCorner[0] = y
                if abs(x - result['rightShoulderCorner'][1]) < abs(x - result['leftShoulderCorner'][1]) \
                        and rightNeckCorner[0] > y:
                    rightNeckCorner[1] = x
                    rightNeckCorner[0] = y
    result['leftNeckCorner'] = leftNeckCorner
    result['rightNeckCorner'] = rightNeckCorner

    maskWithoutCollar = foregroundMaskWithoutCollar(foreground_mask_im, result)

    return result, maskWithoutCollar
