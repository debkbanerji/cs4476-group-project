import numpy as np


def resize(image, targetShape, backgroundPixel=None):
    image = np.array(image)
    inputShape = image.shape

    imageContainer = np.zeros(shape=(max(image.shape[0], targetShape[0]), max(image.shape[1], targetShape[1]), 3),
                              dtype=np.uint8)
    energyImageContainer = np.zeros(shape=(imageContainer.shape[0], imageContainer.shape[1]), dtype=np.double)

    imageContainer[:inputShape[0], :inputShape[1]] = image

    getEnergyImage(energyImageContainer, imageContainer, imageContainer.shape, backgroundPixel)

    currShape = [inputShape[0], inputShape[1]]

    while currShape[0] > targetShape[0]:
        print('reducing height: ' + str(
            currShape[0] - targetShape[0]) + ' iterations left')  # TODO: Find better way to log progress
        reduceHeight(imageContainer, energyImageContainer, currShape, backgroundPixel)
        currShape[0] -= 1
    while currShape[1] > targetShape[1]:
        print('reducing width: ' + str(
            currShape[1] - targetShape[1]) + ' iterations left')  # TODO: Find better way to log progress
        reduceWidth(imageContainer, energyImageContainer, currShape, backgroundPixel)
        currShape[1] -= 1
    residualEnergyImageContainer = np.zeros(shape=(imageContainer.shape[0], imageContainer.shape[1]), dtype=np.double)
    while currShape[0] < targetShape[0]:
        print('increasing height: ' + str(
            targetShape[0] - currShape[0]) + ' iterations left')  # TODO: Find better way to log progress
        increaseHeight(imageContainer, energyImageContainer, residualEnergyImageContainer, currShape, backgroundPixel)
        currShape[0] += 1
    while currShape[1] < targetShape[1]:
        print('increasing width: ' + str(
            targetShape[1] - currShape[1]) + ' iterations left')  # TODO: Find better way to log progress
        increaseWidth(imageContainer, energyImageContainer, residualEnergyImageContainer, currShape, backgroundPixel)
        currShape[1] += 1

    outputImage = imageContainer[:targetShape[0], :targetShape[1]]
    return outputImage


def reduceWidth(imageContainer, energyImageContainer, currentImageShape, backgroundPixel):
    M = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)
    MCount = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)

    for i in range(0, currentImageShape[0]):
        for j in range(0, currentImageShape[1]):
            if i > 0:
                minTopIndex = j
                if j > 0 and M[i - 1, minTopIndex] / MCount[i - 1, minTopIndex] \
                        > M[i - 1, j - 1] / MCount[i - 1, j - 1]:
                    minTopIndex = j - 1
                if j < currentImageShape[1] - 1 and M[i - 1, minTopIndex] / MCount[i - 1, minTopIndex] \
                        > M[i - 1, j + 1] / MCount[i - 1, j + 1]:
                    minTopIndex = j + 1
                M[i, j] = max(energyImageContainer[i, j], 0) + M[
                    i - 1, minTopIndex]
                MCount[i, j] = MCount[i - 1, minTopIndex] + (0 if energyImageContainer[i, j] == -1 else 1)
            else:
                M[i, j] = max(energyImageContainer[i, j], 0)
                MCount[i, j] = 1 + (0 if energyImageContainer[i, j] == -1 else 1)
                # always add in 1 for normalization to prevent divide by 0 errors
                # TODO: Use max(MCount value, 1) everywhere instead

    seam = findOptimalVerticalSeam(M / MCount)

    for row in range(0, currentImageShape[0]):
        seamCol = seam[row]

        # shift everything past this column
        for col in range(seamCol + 1, currentImageShape[1]):
            imageContainer[row, col - 1] = imageContainer[row, col]
            energyImageContainer[row, col - 1] = energyImageContainer[row, col]
        imageContainer[row, currentImageShape[1] - 1] = [0, 0, 0]
        energyImageContainer[row, currentImageShape[1] - 1] = 0

        # update pixels of energy image which were formerly adjacent to the removed seam
        if 0 <= seamCol < currentImageShape[1] - 1:
            energyImageContainer[row, seamCol] = getPixelEnergy(imageContainer, currentImageShape, row, seamCol,
                                                                backgroundPixel)
        if 0 <= seamCol - 1 < currentImageShape[1] - 1:
            energyImageContainer[row, seamCol - 1] = getPixelEnergy(imageContainer, currentImageShape, row,
                                                                    seamCol - 1, backgroundPixel)


def reduceHeight(imageContainer, energyImageContainer, currentImageShape, backgroundPixel):
    M = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)
    MCount = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)

    for j in range(0, currentImageShape[1]):
        for i in range(0, currentImageShape[0]):
            if j > 0:
                minLeftIndex = i
                if i > 0 and M[minLeftIndex, j - 1] / MCount[minLeftIndex, j - 1] \
                        > M[i - 1, j - 1] / MCount[i - 1, j - 1]:
                    minLeftIndex = i - 1
                if i < currentImageShape[0] - 1 and M[minLeftIndex, j - 1] / MCount[minLeftIndex, j - 1] \
                        > M[i + 1, j - 1] / MCount[i + 1, j - 1]:
                    minLeftIndex = i + 1
                M[i, j] = max(energyImageContainer[i, j], 0) + M[
                    minLeftIndex, j - 1]
                MCount[i, j] = MCount[minLeftIndex, j - 1] + (0 if energyImageContainer[i, j] == -1 else 1)
            else:
                M[i, j] = max(energyImageContainer[i, j], 0)
                MCount[i, j] = 1 + (0 if energyImageContainer[i, j] == -1 else 1)
                # always add in 1 for normalization to prevent divide by 0 errors

    seam = findOptimalHorizontalSeam(M / MCount)

    for col in range(0, currentImageShape[1]):
        seamRow = seam[col]

        # shift everything past this row
        for row in range(seamRow + 1, currentImageShape[0]):
            imageContainer[row - 1, col] = imageContainer[row, col]
            energyImageContainer[row - 1, col] = energyImageContainer[row, col]
        imageContainer[currentImageShape[0] - 1, col] = [0, 0, 0]
        energyImageContainer[currentImageShape[0] - 1, col] = 0

        # update pixels of energy image which were formerly adjacent to the removed seam
        if 0 <= seamRow < currentImageShape[0] - 1:
            energyImageContainer[seamRow, col] = getPixelEnergy(imageContainer, currentImageShape, seamRow, col,
                                                                backgroundPixel)
        if 0 <= seamRow - 1 < currentImageShape[0] - 1:
            energyImageContainer[seamRow - 1, col] = getPixelEnergy(imageContainer, currentImageShape, seamRow - 1,
                                                                    col, backgroundPixel)


def increaseWidth(imageContainer, energyImageContainer, residualEnergyImageContainer, currentImageShape,
                  backgroundPixel):
    M = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)
    MCount = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)

    for i in range(0, currentImageShape[0]):
        for j in range(0, currentImageShape[1]):
            if i > 0:
                minTopIndex = j
                if j > 0 and M[i - 1, minTopIndex] / MCount[i - 1, minTopIndex] \
                        > M[i - 1, j - 1] / MCount[i - 1, j - 1]:
                    minTopIndex = j - 1
                if j < currentImageShape[1] - 1 and M[i - 1, minTopIndex] / MCount[i - 1, minTopIndex] \
                        > M[i - 1, j + 1] / MCount[i - 1, j + 1]:
                    minTopIndex = j + 1
                M[i, j] = max(energyImageContainer[i, j], 0) + residualEnergyImageContainer[i, j] + M[
                    i - 1, minTopIndex]
                MCount[i, j] = MCount[i - 1, minTopIndex] + (0 if energyImageContainer[i, j] == -1 else 1)
            else:
                M[i, j] = max(energyImageContainer[i, j], 0) + residualEnergyImageContainer[i, j]
                MCount[i, j] = 1 + (0 if energyImageContainer[i, j] == -1 else 1)
                # always add in 1 for normalization to prevent divide by 0 errors

    # decay residualEnergyImageContainer
    residualEnergyImageContainer *= 0.99

    maxEnergy = energyImageContainer.max()

    seam = findOptimalVerticalSeam(M / MCount)

    for row in range(0, currentImageShape[0]):
        seamCol = seam[row]

        # shift everything past this column (duplicating lowest energy seam on the right)
        for col in reversed(range(seamCol + 1, currentImageShape[1] + 1)):
            imageContainer[row, col] = imageContainer[row, col - 1]
            energyImageContainer[row, col] = energyImageContainer[row, col - 1]
            residualEnergyImageContainer[row, col] = residualEnergyImageContainer[row, col - 1]

        # mark this seam in residualEnergyImageContainer so we don't duplicate it again
        residualEnergyImageContainer[row, seamCol] = maxEnergy
        residualEnergyImageContainer[row, seamCol + 1] = maxEnergy

        # update pixels of energy image which were on or to the right of the duplicated seam
        if 0 <= seamCol + 1 < currentImageShape[1] - 1:
            energyImageContainer[row, seamCol + 1] = getPixelEnergy(imageContainer, currentImageShape, row,
                                                                    seamCol + 1, backgroundPixel)
        if 0 <= seamCol + 2 < currentImageShape[1] - 1:
            energyImageContainer[row, seamCol + 2] = getPixelEnergy(imageContainer, currentImageShape, row,
                                                                    seamCol + 2, backgroundPixel)


def increaseHeight(imageContainer, energyImageContainer, residualEnergyImageContainer, currentImageShape,
                   backgroundPixel):
    M = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)
    MCount = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)

    for j in range(0, currentImageShape[1]):
        for i in range(0, currentImageShape[0]):
            if j > 0:
                minLeftIndex = i
                if i > 0 and M[minLeftIndex, j - 1] / MCount[minLeftIndex, j - 1] \
                        > M[i - 1, j - 1] / MCount[i - 1, j - 1]:
                    minLeftIndex = i - 1
                if i < currentImageShape[0] - 1 and M[minLeftIndex, j - 1] / MCount[minLeftIndex, j - 1] \
                        > M[i + 1, j - 1] / MCount[i + 1, j - 1]:
                    minLeftIndex = i + 1
                M[i, j] = max(energyImageContainer[i, j], 0) + residualEnergyImageContainer[i, j] + M[
                    minLeftIndex, j - 1]
                MCount[i, j] = MCount[minLeftIndex, j - 1] + (0 if energyImageContainer[i, j] == -1 else 1)
            else:
                M[i, j] = max(energyImageContainer[i, j], 0) + residualEnergyImageContainer[i, j]
                MCount[i, j] = 1 + (0 if energyImageContainer[i, j] == -1 else 1)
                # always add in 1 for normalization to prevent divide by 0 errors

    # decay residualEnergyImageContainer
    residualEnergyImageContainer *= 0.99

    maxEnergy = energyImageContainer.max()

    seam = findOptimalHorizontalSeam(M / MCount)

    for col in range(0, currentImageShape[1]):
        seamRow = seam[col]

        # shift everything past this row (duplicating lowest energy seam on the bottom)
        for row in reversed(range(seamRow + 1, currentImageShape[0] + 1)):
            imageContainer[row, col] = imageContainer[row - 1, col]
            energyImageContainer[row, col] = energyImageContainer[row - 1, col]
            residualEnergyImageContainer[row, col] = residualEnergyImageContainer[row - 1, col]

        # mark this seam in residualEnergyImageContainer so we don't duplicate it again
        residualEnergyImageContainer[seamRow, col] = maxEnergy
        residualEnergyImageContainer[seamRow + 1, col] = maxEnergy

        # update pixels of energy image which were formerly adjacent to the removed seam
        if 0 <= seamRow + 1 < currentImageShape[0] - 1:
            energyImageContainer[seamRow + 1, col] = getPixelEnergy(imageContainer, currentImageShape, seamRow + 1,
                                                                    col, backgroundPixel)
        if 0 <= seamRow + 2 < currentImageShape[0] - 1:
            energyImageContainer[seamRow + 2, col] = getPixelEnergy(imageContainer, currentImageShape, seamRow + 2,
                                                                    col, backgroundPixel)


def getEnergyImage(energyImageContainer, imageContainer, imageShape, backgroundPixel):
    for i in range(0, imageShape[0]):
        for j in range(0, imageShape[1]):
            energyImageContainer[i, j] = getPixelEnergy(imageContainer, imageShape, i, j, backgroundPixel)


def getPixelEnergy(imageContainer, imageShape, i, j, backgroundPixel):
    if backgroundPixel is not None and getEnergyDiff(imageContainer[i, j], backgroundPixel) < 20:
        return -1  # Mark the pixel as a background pixel
    energy = 0
    if i < imageShape[0] - 1:
        energy += getEnergyDiff(imageContainer[i, j], imageContainer[i + 1, j])
    if j < imageShape[1] - 1:
        energy += getEnergyDiff(imageContainer[i, j], imageContainer[i, j + 1])

    # From a single pixel, it is better to calculate the difference in energy backwards as well as forwards,
    # since this gives us a more accurate idea of what the change in value between a pixel and its surrounding
    # pixels is
    #
    # the potential doubling in magnitude doesn't matter since we're only
    # comparing these values to other values computed in the same way
    if i > 0:
        energy += getEnergyDiff(imageContainer[i, j], imageContainer[i - 1, j])
    if j > 0:
        energy += getEnergyDiff(imageContainer[i, j], imageContainer[i, j - 1])
    return energy


def getEnergyDiff(p1, p2):
    # Note: for calculating energy, we're adding up the difference in values between red, blue and
    # green between the two pixels
    #
    # This way, we can express more information than if we had converted it to grayscale
    # and just compared those differences
    # The values will be higher, but that clearly doesn't matter since we're only
    # comparing these values to other values computed in the same way
    diff = 0
    for i in range(0, 3):
        diff += abs(int(p1[i]) - int(p2[i]))
    return diff


def findOptimalVerticalSeam(cumulativeEnergyMap):
    result = []
    inputShape = cumulativeEnergyMap.shape
    currPoint = [inputShape[0] - 1, 0]
    for i in range(0, inputShape[1]):
        if cumulativeEnergyMap[currPoint[0], i] < cumulativeEnergyMap[currPoint[0], currPoint[1]]:
            currPoint[1] = i
    for i in range(0, inputShape[0]):
        result.append(currPoint[1])
        currPoint[0] -= 1
        bestCol = currPoint[1]
        if currPoint[1] > 0 and cumulativeEnergyMap[currPoint[0], bestCol] > cumulativeEnergyMap[
            currPoint[0], currPoint[1] - 1]:
            bestCol = currPoint[1] - 1
        if currPoint[1] < inputShape[1] - 1 and cumulativeEnergyMap[currPoint[0], bestCol] > cumulativeEnergyMap[
            currPoint[0], currPoint[1] + 1]:
            bestCol = currPoint[1] + 1
        currPoint[1] = bestCol

    result.reverse()
    return result


def findOptimalHorizontalSeam(cumulativeEnergyMap):
    result = []
    inputShape = cumulativeEnergyMap.shape
    currPoint = [0, inputShape[1] - 1]
    for i in range(0, inputShape[0]):
        if cumulativeEnergyMap[i, currPoint[1]] < cumulativeEnergyMap[currPoint[0], currPoint[1]]:
            currPoint[0] = i
    for i in range(0, inputShape[1]):
        result.append(currPoint[0])
        currPoint[1] -= 1
        bestRow = currPoint[0]
        if currPoint[0] > 0 and cumulativeEnergyMap[bestRow, currPoint[1]] > cumulativeEnergyMap[
            currPoint[0] - 1, currPoint[1]]:
            bestRow = currPoint[0] - 1
        if currPoint[0] < inputShape[0] - 1 and cumulativeEnergyMap[bestRow, currPoint[1]] > cumulativeEnergyMap[
            currPoint[0] + 1, currPoint[1]]:
            bestRow = currPoint[0] + 1
        currPoint[0] = bestRow

    result.reverse()
    return result
