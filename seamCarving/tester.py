import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from seamCarving import resize

input_im_filename = 'inputSeamCarvingPrague.jpg'

input_image = np.array(Image.open(input_im_filename))

plt.imshow(input_image)
plt.show()

output_image = resize(input_image, (480, 540))

f, subplot = plt.subplots(1, 2)

subplot[0].imshow(input_image)
subplot[0].set_title('Input Image: (' + str(input_image.shape[0]) + ', ' + str(input_image.shape[1]) + ')')

subplot[1].imshow(output_image)
subplot[1].set_title('Resized Image: (' + str(output_image.shape[0]) + ', ' + str(output_image.shape[1]) + ')')

plt.show()
