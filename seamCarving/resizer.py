import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from seamCarving import resize
import math


def testResize():
    input_im_filename = 'resize-test-shirt.jpg'

    input_image = np.array(Image.open(input_im_filename))

    plt.imshow(input_image)
    plt.show()

    output_image = resize(input_image, (input_image.shape[0] - 100, input_image.shape[1]),
                          backgroundPixel=(255, 255, 255))

    f, subplot = plt.subplots(1, 2)

    subplot[0].imshow(input_image)
    subplot[0].set_title('Input Image: (' + str(input_image.shape[0]) + ', ' + str(input_image.shape[1]) + ')')

    subplot[1].imshow(output_image)
    subplot[1].set_title('Resized Image: (' + str(output_image.shape[0]) + ', ' + str(output_image.shape[1]) + ')')

    plt.show()


def resizeShirt(input_image):
    shirt_torsoPoints = np.load('../pipelining/t_shirt1torsoPoints.npy')
    body_torsoPoints = np.load('../pipelining/torsoPoints.npy')

    shirt_highestPoint = (
    shirt_torsoPoints[0, 1] if shirt_torsoPoints[0, 1] < shirt_torsoPoints[1, 1] else shirt_torsoPoints[1, 1])
    shirt_lowestPoint = (
    shirt_torsoPoints[4, 1] if shirt_torsoPoints[4, 1] > shirt_torsoPoints[5, 1] else shirt_torsoPoints[5, 1])
    shirt_leftmostPoint = shirt_torsoPoints[4, 0]
    shirt_rigtmostPoint = shirt_torsoPoints[5, 0]

    body_highestPoint = (
    body_torsoPoints[0, 1] if body_torsoPoints[0, 1] < body_torsoPoints[1, 1] else body_torsoPoints[1, 1])
    body_lowestPoint = (
    body_torsoPoints[4, 1] if body_torsoPoints[4, 1] > body_torsoPoints[5, 1] else body_torsoPoints[5, 1])
    body_leftmostPoint = body_torsoPoints[4, 0]
    body_rigtmostPoint = body_torsoPoints[5, 0]

    shirt_width = int(shirt_rigtmostPoint - shirt_leftmostPoint)  # x
    shirt_height = int(shirt_lowestPoint - shirt_highestPoint)  # y
    body_width = int(body_rigtmostPoint - body_leftmostPoint)  # a
    body_height = int(body_lowestPoint - body_highestPoint)  # b

    print("shirt - width:" + str(shirt_width) + " by height: " + str(shirt_height))
    print("body - width:" + str(body_width) + " by height: " + str(body_height))

    shirt_aspectRatio = shirt_height / shirt_width  # y/x
    body_aspectRatio = body_height / body_width  # b/a
    # print(shirt_aspectRatio)
    # print(body_aspectRatio)

    backgroundPixel = input_image[0, input_image.shape[1] - 1]  # top right corner

    # calculations for how to find necessary change in shirt width
    #  y/(x+??) = b/a
    #  ay = xb + ??b
    # (ay-xb)/b  = ??
    # (ay)/b - x = ??

    deltaShirtWidth = int((body_width * shirt_height) / body_height) - shirt_width

    # calculations for how to find necessary change in shirt height
    #  (y+??)/(x) = b/a
    #  ay + ??a = xb
    #  ??a = xb - ay
    #  ?? = (xb)/a - y

    deltaShirtHeight = int((shirt_width * body_height) / body_width) - shirt_height

    # based off smaller delta, resize the shirt

    if math.fabs(deltaShirtHeight) > math.fabs(deltaShirtWidth):
        # resize by adding width
        output_image = resize(input_image, (input_image.shape[0], input_image.shape[1] + deltaShirtWidth),
                              backgroundPixel=backgroundPixel)
    else:
        # resize by adding height
        output_image = resize(input_image, (input_image.shape[0] + deltaShirtHeight, input_image.shape[1]),
                              backgroundPixel=backgroundPixel)

    plt.imsave('shirt_updatedAspectRatio.png', output_image)


def main():
    input_im_filename = 'resize-test-shirt.jpg'
    input_image = np.array(Image.open(input_im_filename))
    resizeShirt(input_image)


if __name__ == "__main__":
    main();
