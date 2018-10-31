from skimage import color, filters, exposure
from scipy import misc, ndimage
import matplotlib.pyplot as plt
import numpy as np
from urllib.request import urlopen


def foregroundMask(shirtImg, imageName):
    maxShirtVal = np.max(shirtImg)
    shirtImgScaled = shirtImg * 255 / maxShirtVal
    grayIm = color.rgb2gray(shirtImgScaled)
    grayIm = filters.apply_hysteresis_threshold(grayIm, 0.15, 0.35)

    sobelEdges = filters.sobel(grayIm)
    filledEdges = np.array(ndimage.binary_fill_holes(sobelEdges), dtype=np.bool)
    if filledEdges[0, 0] == True:
        filledEdges = np.logical_not(filledEdges)
        # want the top left corner (which denotes background) to be marked as False

    # print(np.unique(filledEdges))
    np.save(str(imageName) + "ForegroundMask.npy", filledEdges)
    return filledEdges
    # plt.subplot(121)
    # plt.imshow(shirtImg)
    # plt.subplot(122)
    # plt.imshow(filledEdges)
    # plt.show()


# url = "https://image.freepik.com/free-vector/white-tshirt-mock-up-on-black-background_6735-98.jpg"
# with urlopen(url) as file:
#     myTshirt = misc.imread(file, mode="RGBA")
# blackShirt = misc.imread("../proposal/assets/images/black-shirt.png", mode="RGBA")
# blueShirt = misc.imread("../proposal/assets/images/blue-shirt.jpg", mode="RGBA")
# fancyVest = misc.imread("../proposal/assets/images/fancy-vest.png", mode="RGBA")
# diamondSweater = misc.imread("../proposal/assets/images/diamond-sweater.png", mode="RGBA")
# greyShirt = misc.imread("../proposal/assets/images/grey-shirt.png", mode="RGBA")
#
# shirtsList = [myTshirt, blackShirt, blueShirt, fancyVest, diamondSweater, greyShirt]
#
# for i, shirt in enumerate(shirtsList):
#     result = foregroundMask(shirt, "shirt" + str(i))
#     print(result)

