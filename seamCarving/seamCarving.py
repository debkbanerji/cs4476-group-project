import numpy as np
import matplotlib.pyplot as plt


def resize(image, targetShape):
    image = np.array(image)
    inputShape = image.shape

    imageContainer = np.zeros(shape=(max(image.shape[0], targetShape[0]), max(image.shape[1], targetShape[1]), 3),
                              dtype=np.uint8)
    energyImageContainer = np.zeros(shape=(imageContainer.shape[0], imageContainer.shape[1]), dtype=np.double)

    imageContainer[:inputShape[0], :inputShape[1]] = image

    energy_image(energyImageContainer, imageContainer, imageContainer.shape)

    currShape = [inputShape[0], inputShape[1]]

    while currShape[0] > targetShape[0]:
        print('reducing height: ' + str(
            currShape[0] - targetShape[0]) + ' iterations left')  # TODO: Find better way to log progress
        reduceHeight(imageContainer, energyImageContainer, currShape)
        currShape[0] -= 1
    while currShape[1] > targetShape[1]:
        print('reducing width: ' + str(
            currShape[1] - targetShape[1]) + ' iterations left')  # TODO: Find better way to log progress
        reduceWidth(imageContainer, energyImageContainer, currShape)
        currShape[1] -= 1
    while currShape[0] < targetShape[0]:
        increaseHeight(imageContainer, energyImageContainer, currShape)
        currShape[0] += 1
    while currShape[1] < targetShape[1]:
        increaseWidth(imageContainer, energyImageContainer, currShape)
        currShape[1] += 1

    outputImage = imageContainer[:targetShape[0], :targetShape[1]]
    return outputImage


def reduceWidth(imageContainer, energyImageContainer, currentImageShape):
    M = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)

    for i in range(0, currentImageShape[0]):
        for j in range(0, currentImageShape[1]):
            minTopEnergy = 0
            if i > 0:
                minTopEnergy = M[i - 1, j]
                if j > 0:
                    minTopEnergy = min(minTopEnergy, M[i - 1, j - 1])
                if j < currentImageShape[1] - 1:
                    minTopEnergy = min(minTopEnergy, M[i - 1, j + 1])

            M[i, j] = energyImageContainer[i, j] + minTopEnergy

    # plt.imshow(M)
    # plt.show()

    seam = find_optimal_vertical_seam(M)

    for row in range(0, currentImageShape[0]):
        seam_col = seam[row]

        # shift everything past this column
        for col in range(seam_col + 1, currentImageShape[1]):
            imageContainer[row, col - 1] = imageContainer[row, col]
            energyImageContainer[row, col - 1] = energyImageContainer[row, col]
        imageContainer[row, currentImageShape[1] - 1] = [0, 0, 0]
        energyImageContainer[row, currentImageShape[1] - 1] = 0

        # update pixels of energy image which were formerly adjacent to the removed seam
        if 0 <= seam_col < currentImageShape[1] - 1:
            energyImageContainer[row, seam_col] = get_pixel_energy(imageContainer, currentImageShape, row, seam_col)
        if 0 <= seam_col - 1 < currentImageShape[1] - 1:
            energyImageContainer[row, seam_col - 1] = get_pixel_energy(imageContainer, currentImageShape, row,
                                                                       seam_col - 1)


def reduceHeight(imageContainer, energyImageContainer, currentImageShape):
    M = np.zeros(shape=(currentImageShape[0], currentImageShape[1]), dtype=np.double)

    for j in range(0, currentImageShape[1]):
        for i in range(0, currentImageShape[0]):
            minLeftEnergy = 0
            if j > 0:
                minLeftEnergy = M[i, j - 1]
                if i > 0:
                    minLeftEnergy = min(minLeftEnergy, M[i - 1, j - 1])
                if i < currentImageShape[0] - 1:
                    minLeftEnergy = min(minLeftEnergy, M[i + 1, j - 1])
            M[i, j] = energyImageContainer[i, j] + minLeftEnergy

    seam = find_optimal_horizontal_seam(M)

    for col in range(0, currentImageShape[1]):
        seam_row = seam[col]

        # shift everything past this row
        for row in range(seam_row + 1, currentImageShape[0]):
            imageContainer[row - 1, col] = imageContainer[row, col]
            energyImageContainer[row - 1, col] = energyImageContainer[row, col]
        imageContainer[currentImageShape[0] - 1, col] = [0, 0, 0]
        energyImageContainer[currentImageShape[0] - 1, col] = 0

        # update pixels of energy image which were formerly adjacent to the removed seam
        if 0 <= seam_row < currentImageShape[0] - 1:
            energyImageContainer[seam_row, col] = get_pixel_energy(imageContainer, currentImageShape, seam_row, col)
        if 0 <= seam_row - 1 < currentImageShape[0] - 1:
            energyImageContainer[seam_row - 1, col] = get_pixel_energy(imageContainer, currentImageShape, seam_row - 1,
                                                                       col)
    pass


def increaseWidth(imageContainer, energyImageContainer, currentImageShape):
    # TODO: Implement
    pass


def increaseHeight(imageContainer, energyImageContainer, currentImageShape):
    # TODO: Implement
    pass


def energy_image(energyImageContainer, imageContainer, imageShape):
    for i in range(0, imageShape[0]):
        for j in range(0, imageShape[1]):
            energyImageContainer[i, j] = get_pixel_energy(imageContainer, imageShape, i, j)


def get_pixel_energy(imageContainer, imageShape, i, j):
    energy = 0
    if i < imageShape[0] - 1:
        energy += energy_diff(imageContainer[i, j], imageContainer[i + 1, j])
    if j < imageShape[1] - 1:
        energy += energy_diff(imageContainer[i, j], imageContainer[i, j + 1])

    # From a single pixel, it is better to calculate the difference in energy backwards as well as forwards,
    # since this gives us a more accurate idea of what the change in value between a pixel and its surrounding
    # pixels is
    #
    # the potential doubling in magnitude doesn't matter since we're only
    # comparing these values to other values computed in the same way
    if i > 0:
        energy += energy_diff(imageContainer[i, j], imageContainer[i - 1, j])
    if j > 0:
        energy += energy_diff(imageContainer[i, j], imageContainer[i, j - 1])
    return energy


def energy_diff(p1, p2):
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


def find_optimal_vertical_seam(cumulativeEnergyMap):
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


def find_optimal_horizontal_seam(cumulativeEnergyMap):
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
