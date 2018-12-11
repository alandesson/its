import math
import urllib3
import json
import certifi
import codecs
import datetime
#import pickle
import os
import psutil
import cv2
process = psutil.Process(os.getpid())


#Save/Load Requests
# def Save(path,data):
# 	with open(path, 'wb') as handle:
# 		pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
#
# def Load(path):
# 	with open(path, 'rb') as handle:
# 		return pickle.load(handle)

def getPointLatLng(x, y, lat, lng, zoom, w, h):
    parallelMultiplier = math.cos(lat * math.pi / 180.0)
    degreesPerPixelX = 360.0 / math.pow(2, zoom + 8)
    degreesPerPixelY = 360.0 / math.pow(2, zoom + 8) * parallelMultiplier
    pointLat = lat - degreesPerPixelY * (y - h / 2.0)
    pointLng = lng + degreesPerPixelX * (x - w / 2.0)

    return (pointLat, pointLng)

def isValid(list,ret):
    base = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    key = '&key=AIzaSyDz-ETRL2NWIgre2ha8NAzat-npHnxlz4o'

    origin = str(list[0][0]) + ',' + str(list[0][1])
    dest = str(list[1][0]) + ',' + str(list[1][1])

    request = base + 'units=metric'
    request += '&origins=' + origin
    request += '&destinations=' + dest
    request += '&departure_time=1540350000'
    request += '&traffic_model=optimistic'
    request += key

    j = {}
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
    reader = codecs.getreader('utf-8')

    try:
        print(request)
        res = http.request('GET',request,preload_content=False)
        j = json.load(reader(res))
    except Exception as e:
        print(e)
        return False
    else:
        print("success")
        print(j)
        dst = j['rows'][0]['elements'][0]['distance']['value']
        tmp1 = j['rows'][0]['elements'][0]['duration']['value']
        tmp2 = j['rows'][0]['elements'][0]['duration_in_traffic']['value']

        ret.append(dst)
        ret.append(tmp1)
        ret.append(tmp2)

    return True

e1 = cv2.getTickCount()

#configurações do request - dados para conversão
w = 640
h = 640
zoom = 20
lat = -10.9709826
lng = -37.0651128

finalArestas = []
with open('../arestas_final.txt', 'r') as file:
    counter = 0
    for line in file:
        lista = line.split(',')
        lista[-1] = lista[-1].split()[0]
        numList = [int(n) for n in lista]

        coordList = []
        i = 0
        while i < len(numList):
            x = numList[i] - 10560 #imagem coletada deslocada 320 pixel
            y = numList[i + 1] - 10560 #consertar coleta
            coordList.append(getPointLatLng(y,x,lat,lng,zoom,w,h))

            i += 2

        if isValid(coordList,numList):
            if len(numList) > 4:
                finalArestas.append([numList[0],numList[1],numList[2],numList[3],numList[4],numList[5],numList[6]])
        else:
            break

        counter += 1
        print("aresta ",counter)

timestamp = datetime.datetime.now().strftime("%I%M%p-%B-%d-%Y")
with open('../arestas_optimistic_3h4F.txt', 'w') as file:
    for aresta in finalArestas:
        string = str(aresta[0]) + "," + str(aresta[1]) + ","
        string += str(aresta[2]) + "," + str(aresta[3]) + ","
        string += str(aresta[4]) + "," + str(aresta[5]) + ","
        string += str(aresta[6]) + "\n"
        file.write(string)

# #Code Excution Timer
e2 = cv2.getTickCount()
time = (e2 - e1) / cv2.getTickFrequency()
print('Performance: ', time, 's')

with process.oneshot():
    print(process.memory_info().rss/1048576, "mb")

