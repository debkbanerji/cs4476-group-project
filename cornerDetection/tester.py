from PIL import Image

import numpy as np
import matplotlib.pyplot as plt

from cornerDetection.backgroundRemover import foregroundMask
from cornerDetection.cornerDetector import getShirtCorners, getAllCorners

input_im_filenames = ['../proposal/assets/images/black-shirt.png', '../proposal/assets/images/blue-shirt.jpg']

f, subplot = plt.subplots(len(input_im_filenames), 4)
f.suptitle('Testing corner detection and assignment')

for i in range(0, len(input_im_filenames)):
    input_im_filename = input_im_filenames[i]
    input_image = np.array(Image.open(input_im_filename))
    subplot[i][0].imshow(input_image)

    background_image = foregroundMask(input_image)
    subplot[i][1].imshow(background_image)

    all_harris_corners = getAllCorners(input_image)

    subplot[i][2].imshow(input_image)
    if len(all_harris_corners) > 0:
        subplot[i][2].scatter(all_harris_corners[:, 1], all_harris_corners[:, 0])

    target_corners = getShirtCorners(input_image)
    target_corner_list = []
    for key, val in target_corners.items():
        target_corner_list.append(val)
    target_corner_list = np.array(target_corner_list)

    subplot[i][3].imshow(input_image)
    if len(target_corners) > 0:
        subplot[i][3].scatter(target_corner_list[:, 1], target_corner_list[:, 0])

plt.show()
