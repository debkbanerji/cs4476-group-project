from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
import re

from cornerDetection.backgroundRemover import foregroundMask
from cornerDetection.cornerDetector import getShirtCorners, getAllCorners

input_im_filenames = [
    '../proposal/assets/images/blue-shirt.jpg',
    '../pipelining/images/catShirt.jpeg',
    '../pipelining/images/usaShirt.jpeg',
    '../proposal/assets/images/black-shirt.png',
    '../pipelining/images/referenceTorso.png',
]

for i in range(0, len(input_im_filenames)):
    f, subplot = plt.subplots(2, 2)
    f.suptitle('Corner detection and assignment algorithm visualization')

    input_im_filename = input_im_filenames[i]
    input_image = np.array(Image.open(input_im_filename))
    subplot[0][0].imshow(input_image)
    subplot[0][0].axis('off')
    subplot[0][0].set_title('Input Image')

    background_image = foregroundMask(input_image)
    subplot[0][1].imshow(background_image)
    subplot[0][1].axis('off')
    subplot[0][1].set_title('Extracted Foreground')

    all_harris_corners = getAllCorners(background_image)

    subplot[1][0].imshow(input_image)
    subplot[1][0].axis('off')
    subplot[1][0].set_title('Detected Corners (Harris)')
    if len(all_harris_corners) > 0:
        subplot[1][0].scatter(all_harris_corners[:, 1], all_harris_corners[:, 0])

    target_corners = getShirtCorners(input_image)
    target_corner_list = []
    labelShorteningRegex = re.compile(r"(?<!^)[^A-Z]")
    for key, val in target_corners.items():
        target_corner_list.append(val)
        displayKey = re.sub(labelShorteningRegex, '', str(key))
        subplot[1][1].annotate(displayKey, (val[1], val[0]))
    target_corner_list = np.array(target_corner_list)

    subplot[1][1].imshow(input_image)
    subplot[1][1].axis('off')
    subplot[1][1].set_title('Final Detected and Labelled corners')
    if len(target_corners) > 0:
        subplot[1][1].scatter(target_corner_list[:, 1], target_corner_list[:, 0])

    plt.show()
