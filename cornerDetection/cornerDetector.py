import numpy as np
from skimage.feature import corner_harris, corner_peaks
from cornerDetection.backgroundRemover import foregroundMask
import matplotlib.pyplot as plt
from sklearn.cluster import MiniBatchKMeans
import cv2

k = 0.05


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
        if result['leftSleeveTopCorner'][0] < corner[0] < result['bottomLeftCorner'][0] - pointSeparationDelta0 \
                and result['leftSleeveTopCorner'][1] + pointSeparationDelta1 < corner[1] < \
                result['rightSleeveTopCorner'][1] - pointSeparationDelta1:
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
                if -1 * shoulderXMult * x + shoulderYMult * y > -1 * shoulderXMult * leftShoulderCorner[
                    1] + shoulderYMult * leftShoulderCorner[0]:
                    leftShoulderCorner[1] = x
                    leftShoulderCorner[0] = y
                if shoulderXMult * x + shoulderYMult * y > shoulderXMult * rightShoulderCorner[1] + shoulderYMult * \
                        rightShoulderCorner[0]:
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
    return result


def getModelShirtCorners(model_im, topLeftCoords, bottomRightCoords, quantizationCount=7):
    quantized_model_im = quantize(model_im, quantizationCount)
    shirt_im = quantized_model_im[topLeftCoords[0]:bottomRightCoords[0], topLeftCoords[1]:bottomRightCoords[1]]
    plt.imshow(shirt_im)
    plt.show()


def quantize(origImg, k):
    # Code adapted from https://www.pyimagesearch.com/2014/07/07/color-quantization-opencv-using-k-means-clustering/
    # (for faster runtime than the version we implemented for the problem set, though this version is a little less 'correct' due to the version of k means used)
    (h, w) = origImg.shape[:2]

    # convert the image from the RGB color space to the L*a*b*
    # color space -- since we will be clustering using k-means
    # which is based on the euclidean distance, we'll use the
    # L*a*b* color space where the euclidean distance implies
    # perceptual meaning
    image = cv2.cvtColor(origImg, cv2.COLOR_BGR2LAB)

    # reshape the image into a feature vector so that k-means
    # can be applied
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # apply k-means using the specified number of clusters and
    # then create the quantized image based on the predictions
    clt = MiniBatchKMeans(n_clusters=k)
    labels = clt.fit_predict(image)
    quant = clt.cluster_centers_.astype("uint8")[labels]

    # reshape the feature vectors to images
    quant = quant.reshape((h, w, 3))

    # convert from L*a*b* to RGB
    quant = cv2.cvtColor(quant, cv2.COLOR_LAB2BGR)

    # display the images and wait for a keypress
    return quant
