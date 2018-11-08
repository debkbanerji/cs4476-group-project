from backgroundRemover import foregroundMask
from PIL import Image
import os

import numpy as np
import matplotlib.pyplot as plt

input_im_filenames = ['../proposal/assets/images/black-shirt.png', '../proposal/assets/images/blue-shirt.jpg']

f, subplot = plt.subplots(len(input_im_filenames), 3)
f.suptitle('Testing corner detection and assignment')

for i in range(0, len(input_im_filenames)):
    input_im_filename = input_im_filenames[i]
    input_image = np.array(Image.open(input_im_filename))
    subplot[i][0].imshow(input_image)

    background_image = foregroundMask(input_image)
    subplot[i][1].imshow(background_image)

plt.show()
