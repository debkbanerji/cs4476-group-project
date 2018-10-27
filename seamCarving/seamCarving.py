import numpy as np


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
        reduceWidth(imageContainer, energyImageContainer, currShape)
        currShape[0] -= 1
    while currShape[1] > targetShape[1]:
        reduceHeight(imageContainer, energyImageContainer, currShape)
        currShape[1] -= 1
    while currShape[0] < targetShape[0]:
        increaseWidth(imageContainer, energyImageContainer, currShape)
        currShape[0] += 1
    while currShape[1] < targetShape[1]:
        increaseHeight(imageContainer, energyImageContainer, currShape)
        currShape[1] += 1

    outputImage = imageContainer[:targetShape[0], :targetShape[1]]
    return outputImage


def reduceWidth(imageContainer, energyImageContainer, currentImageShape):
    # TODO: Implement
    pass


def reduceHeight(imageContainer, energyImageContainer, currentImageShape):
    # TODO: Implement
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

                energyImageContainer[i, j] = energy


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
