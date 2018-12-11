import cv2
import numpy as np

# img = cv2.imread('C:/Users/Alandesson/PycharmProjects/its_project/imgs/lenna.png')
# gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# cv2.imwrite('C:/Users/Alandesson/PycharmProjects/its_project/imgs/gray_lenna.png',gray_image)
# ret,thresh = cv2.threshold(gray_image,127,255,cv2.THRESH_BINARY)
# cv2.imwrite('C:/Users/Alandesson/PycharmProjects/its_project/imgs/threshold_lenna.png',thresh)
# cv2.imshow('gray_image',thresh)
# cv2.waitKey(0)                 # Waits forever for user to press any key
# cv2.destroyAllWindows()        # Closes displayed windows


coord1 = (3873,18404,4528,18372)
coord2 = (4528,18372,3873,18404)

flux1 = -1;
flux2 = -1;

with open('../arestas_final-0127PM-October-21-2018.txt', 'r') as file:
    counter = 0
    for line in file:
        lista = line.split(',')
        lista[-1] = lista[-1].split()[0]
        numList = [int(n) for n in lista]

        test1 = True
        test2 = True
        for i in range(0,4):
            if(coord1[i] != numList[i]):
                test1 = False;
            if(coord2[i] != numList[i]):
                test2 = False;

        if(test1):
            flux1 = numList[-1]/numList[-2]

        if (test2):
            flux2 = numList[-1]/numList[-2]

print('Flux 1:',flux1)
print('Flux 2:',flux2)
print('Ajusting Flux')

sumF = flux1 + flux2
new_flux1 = int(flux1/sumF*80) + 20
new_flux2 = int(flux2/sumF*80) + 20

print('New Flux 1:',new_flux1)
print('New Flux 2:',new_flux2)
