from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
import re

from cornerDetection.cornerDetector import getModelShirtCorners, getAllCorners

input_im_data = [
    ['../pipelining/images/kirtan_img.jpg', (525, 85), (1800, 1280)],
]

for i in range(0, len(input_im_data)):
    f, subplot = plt.subplots(2, 2)
    f.suptitle('Shirt detection and corner algorithm visualization')

    input_im_i_data = input_im_data[i]
    input_im_filename = input_im_i_data[0]
    input_image = np.array(Image.open(input_im_filename))

    target_corners = getModelShirtCorners(input_image, input_im_i_data[1], input_im_i_data[2])

    # TODO: Visualize
