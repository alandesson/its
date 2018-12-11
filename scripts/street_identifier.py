import numpy as np
from PIL import Image
import math
import urllib3
Image.MAX_IMAGE_PIXELS = None
import codecs
import json
import certifi

w = 640
h = 640
zoom = 20
lat = -10.9709826
lng = -37.0651128


def street_name(pnt):
    base = 'https://maps.googleapis.com/maps/api/geocode/json?'
    key = '&key=AIzaSyB7nyIheF1mtkuagOEoGMpKExs0d_PzYvU'
    location = 'latlng=' + str(pnt[0]) + ',' + str(pnt[1])

    request = base + location + key

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
    reader = codecs.getreader('utf-8')

    try:
        # print(request)
        res = http.request('GET',request,preload_content=False)
        j = json.load(reader(res))
    except Exception as e:
        print(e)
    else:
        # print("success")
        for elem in j['results'][0]['address_components']:
            if(elem['types'][0] == 'route'):
                return elem['short_name']

    return 'Not Found'

def getPointLatLng(x, y, lat, lng, zoom, w, h):
    parallelMultiplier = math.cos(lat * math.pi / 180)
    degreesPerPixelX = 360.0 / math.pow(2, zoom + 8)
    degreesPerPixelY = 360.0 / math.pow(2, zoom + 8) * parallelMultiplier
    pointLat = lat - degreesPerPixelY * (y - h / 2)
    pointLng = lng + degreesPerPixelX * (x - w / 2)

    return (pointLat, pointLng)

points = []
with open('../arestas.txt', 'r') as file:
    counter = 0
    for line in file:
        lista = line.split(',')
        lista[-1] = lista[-1].split()[0]
        pnt = (int(lista[3]),int(lista[2]))
        if pnt not in points:
            points.append(pnt)

im = Image.open('../imgs/heatmap.png')

for p in points:
    _,g,_ = im.getpixel(p)
    perc = 100 - (g*100-100)/254.0
    coord = getPointLatLng(p[0]- 10560,p[1]- 10560,lat,lng,zoom,w,h)
    address = street_name(coord)
    address += " está com %.3f" % perc
    address += "% do fluxo em (Lat,Lng:"
    address += str(coord) + ")"
    print(address)

