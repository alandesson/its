# -*- coding: utf-8 -*-

import cv2
import numpy as np
import math
import sys
import requests
import pickle
import gc
from skimage.morphology import skeletonize_3d
from PIL import Image
import os
import psutil
process = psutil.Process(os.getpid())
from subprocess import Popen, PIPE
#from signal import signal, SIGPIPE, SIG_DFL


# Save/Load Requests
def Save(path, data):
    with open(path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def Load(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)


def SimpleImageRequester(path, lat, lng, zoom, w, h):
    base = 'https://maps.googleapis.com/maps/api/staticmap?'
    size = 'size=' + str(w) + 'x' + str(h)
    zoom_str = '&zoom=' + str(zoom)
    coord = '&center=' + str(lat) + ',' + str(lng)
    style = '&style=feature:road|color:0x00ff00&style=feature:landscape|visibility:off&style=element:labels|visibility:off&style=feature:road.arterial|element:labels|visibility:off'
    key = '&key=AIzaSyBswlrOVwtmjg6ito5sUDA4WCEqysqBCDk'

    request = base + size + zoom_str + coord + style + key

    print(request)

    img_data = requests.get(request).content
    with open('C:/Users/Alandesson/PycharmProjects/its_project/imgs/unfiltered/' + path + '.png', 'wb') as handler:
        handler.write(img_data)


def SplitImageRequester(path, lat, lng, zoom, zoomInc, w, h):
    realZoom = zoom + zoomInc
    splits = 2 ** zoomInc
    ind_i = 0
    for i in range(-splits // 2, splits // 2 + int(math.ceil(22.0 * splits / h))):
        ind_j = 0
        for j in range(-splits // 2, splits // 2):
            pathAux = 'splited/' + path + '_(' + str(ind_i) + ',' + str(ind_j) + ')'
            latAux, lngAux = getPointLatLng(j * w, i * h - 22 * ind_i, lat, lng, realZoom, w, h)
            SimpleImageRequester(pathAux, latAux, lngAux, realZoom, w, h)
            ind_j += 1
        ind_i += 1


def imageJoin(path, splits, w, h):
    pathAux = 'C:/Users/Alandesson/PycharmProjects/its_project/imgs/unfiltered/splited/' + path + '_('

    width = w * splits
    height = h * splits

    new_im = Image.new('RGB', (width, height))

    counter = 0
    x_offset = 0
    y_offset = 0
    for i in range(0, splits + int(math.ceil(22.0 * splits / h))):
        for j in range(0, splits):
            pathf = pathAux + str(i) + ',' + str(j) + ').png'
            im = Image.open(pathf)

            new_im.paste(im, (x_offset, y_offset))
            x_offset += w

            counter += 1
            if counter == splits:
                y_offset += h - 22
                x_offset = 0
                counter = 0

            im.close()

    new_im.save('C:/Users/Alandesson/PycharmProjects/its_project/imgs/unfiltered/' + path + '.png')


# neighborhood
def nb4(x, y):
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def pntsInsideCirc(radius):
    pnts = []
    r2 = radius * radius
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if (r2 >= i * i + j * j):
                pnts.append((i, j))

    return pnts


def ImageProcessing(img):
    height, width, channels = img.shape

    # Turning Everything black except streets
    img[np.where((img != [0, 255, 0]).all(axis=2))] = [0, 0, 0]
    # Turning Streets white
    img[np.where((img >= [0, 250, 0]).all(axis=2))] = [255, 255, 255]

    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # find all your connected components
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=8)
    # connectedComponentswithStats yields every seperated component with information on each of them, such as size
    # the following part is just taking out the background which is also considered a component, but most of the time we don't want that.
    sizes = stats[1:, -1];
    nb_components = nb_components - 1

    # minimum size of particles we want to keep (number of pixels)
    # here, it's a fixed value, but you can set it as you want, eg the mean of the sizes or whatever

    max_pos = 0
    # your answer image
    img2 = np.zeros((output.shape))
    # for every component in the image, you keep only the biggest
    img2[output == 1] = 255
    for i in range(1, nb_components):
        if sizes[i] >= sizes[max_pos]:
            img2[output == max_pos + 1] = 0
            img2[output == i + 1] = 255
            max_pos = i

    cv2.imwrite('C:/Users/Alandesson/PycharmProjects/its_project/imgs/unfiltered/map_gray.png', img2)


def skeletonize(img):
    bin_mask = img[:, :, 0] > 100
    skeleton3d = skeletonize_3d(bin_mask)
    path = 'C:/Users/Alandesson/PycharmProjects/its_project/imgs/unfiltered/skeleton.png'
    cv2.imwrite(path, skeleton3d)

    # p = Popen(['./output ' + path], shell=True, stdout=PIPE, stdin=PIPE)
    #
    # img2 = cv2.imread('./imgs/unfiltered/dots.png')
    # dots = np.where((img2 == [255, 255, 255]).all(axis=2))

    # return (dots, skeleton3d)


def getPointLatLng(x, y, lat, lng, zoom, w, h):
    parallelMultiplier = math.cos(lat * math.pi / 180)
    degreesPerPixelX = 360 / math.pow(2, zoom + 8)
    degreesPerPixelY = 360 / math.pow(2, zoom + 8) * parallelMultiplier
    pointLat = lat - degreesPerPixelY * (y - h / 2)
    pointLng = lng + degreesPerPixelX * (x - w / 2)

    return (pointLat, pointLng)


# ---Main---

# Code Excution Timer
e1 = cv2.getTickCount()

w = 640
h = 640
zoom = 15
zoomInc = 5
# Farolandia
# lat = -10.9709826
# lng = -37.0651128

# centro

# print('Colecting Image')
# SplitImageRequester('map',lat,lng,zoom,zoomInc,w,h)
# gc.collect()
imageJoin('map',2**zoomInc,w,h)
print('Processing Image')
img = cv2.imread('C:/Users/Alandesson/PycharmProjects/its_project/imgs/unfiltered/map.png')
ImageProcessing(img)
img = cv2.imread('C:/Users/Alandesson/PycharmProjects/its_project/imgs/unfiltered/map_gray.png')
skeletonize(img)

'''
print('Getting Lat Log Data')
coord = [getPointLatLng(y, x, lat, lng, zoom, w, h) for (x, y) in dots]

print('Saving Pickles')
Save("./pickles/dots.p", dots)
Save("./pickles/coord.p", coord)
Save("./pickles/skeleton.p", skeleton)
'''

with process.oneshot():
    print(process.memory_info().rss/1048576, "mb")

# #Code Excution Timer
e2 = cv2.getTickCount()
time = (e2 - e1) / cv2.getTickFrequency()
print('Performance: ', time, 's')
