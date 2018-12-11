import numpy as np
import cv2

red = cv2.imread('../imgs/heat2359.png')

# white = red.copy()
#
# red[np.where((red != [0, 0, 255]).any(axis=2))] = [0, 0, 0]
# white[np.where((white != [255, 255, 255]).any(axis=2))] = [0, 0, 0]
#
kernel = np.ones((5, 5), np.uint8)

red = cv2.dilate(red,kernel,iterations = 2)
# white = cv2.dilate(white,kernel,iterations = 4)
# white = cv2.bitwise_not(white)
# white[np.where((red == [0, 0, 255]).all(axis=2))] = [0, 0, 255]

cv2.imwrite('../imgs/heat2359_dil.png',red)
# cv2.waitKey(0)
# cv2.destroyAllWindows()