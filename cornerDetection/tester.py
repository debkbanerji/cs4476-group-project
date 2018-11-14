from PIL import Image

import numpy as np
import matplotlib.pyplot as plt

from cornerDetection.backgroundRemover import foregroundMask
from cornerDetection.cornerDetector import getShirtCorners, getAllCorners

input_im_filenames = [
    '../proposal/assets/images/black-shirt.png',
    '../proposal/assets/images/blue-shirt.jpg',
    '../pipelining/images/catShirt.jpeg',
    '../pipelining/images/usaShirt.jpeg',
    '../pipelining/images/referenceTorso.png',
]

f, subplot = plt.subplots(len(input_im_filenames), 4)
f.suptitle('Corner detection and assignment algorithm visualization')

for i in range(0, len(input_im_filenames)):
    input_im_filename = input_im_filenames[i]
    input_image = np.array(Image.open(input_im_filename))
    subplot[i][0].imshow(input_image)
    subplot[i][0].axis('off')
    subplot[i][0].set_title('Input Image')

    background_image = foregroundMask(input_image)
    subplot[i][1].imshow(background_image)
    subplot[i][1].axis('off')
    subplot[i][1].set_title('Extracted Foreground')

    all_harris_corners = getAllCorners(background_image)

    subplot[i][2].imshow(input_image)
    subplot[i][2].axis('off')
    subplot[i][2].set_title('Detected Corners (Harris)')
    if len(all_harris_corners) > 0:
        subplot[i][2].scatter(all_harris_corners[:, 1], all_harris_corners[:, 0])

    target_corners = getShirtCorners(input_image)
    target_corner_list = []
    for key, val in target_corners.items():
        target_corner_list.append(val)
        subplot[i][3].annotate(str(key), (val[1], val[0]))
    target_corner_list = np.array(target_corner_list)

    subplot[i][3].imshow(input_image)
    subplot[i][3].axis('off')
    subplot[i][3].set_title('Final Detected and Labelled corners')
    if len(target_corners) > 0:
        subplot[i][3].scatter(target_corner_list[:, 1], target_corner_list[:, 0])

plt.show()
