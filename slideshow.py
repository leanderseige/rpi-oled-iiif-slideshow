# -*- coding:UTF-8 -*-

import wget
import requests
import urllib.request
import numpy as np
import os
import cv2
import json
import math

#--------------Driver Library-----------------#
import RPi.GPIO as GPIO
import OLED_Driver as OLED
#--------------Image Library---------------#
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageColor
#-------------Test Display Functions---------------#


def Display_Picture(File_Name):
    image = Image.open(File_Name)
    OLED.Display_Image(image)
    
def url_to_image(url):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def analyze_images(image):
    faceCascadef = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_alt.xml")
    facesf = faceCascadef.detectMultiScale(
        image,
        minNeighbors=6,
        minSize=(20, 20)
    )
    faceCascadep = cv2.CascadeClassifier("haarcascades/haarcascade_profileface.xml")
    facesp = faceCascadep.detectMultiScale(
        image,
        minNeighbors=6,
        minSize=(20, 20)
    )
    faces=[*facesf,*facesp]
    return faces

#----------------------MAIN-------------------------#

cola = ["https://iiif.manducus.net/collections/0020/collection.json"] # MKK Dortmund
colb = ["https://iiif.manducus.net/collections/0019/collection.json"] # Burg Posterstein
colc = ["https://iiif.manducus.net/collections/0008/collection.json"] # Städel Museum
cold = ["https://wellcomelibrary.org/service/collections/genres/Group%20portraits/"]
cole = ["https://wellcomelibrary.org/service/collections/genres/Portrait%20prints/"]
colf = ["https://wellcomelibrary.org/service/collections/genres/Portrait%20paintings/"]

cols = [*cola,*colb,*colc,*cold,*cole,*colf]

font = ImageFont.truetype('UbuntuMono-Bold.ttf',12)

try:
    def main():
        OLED.Device_Init()
        while True:
            for cu in cols:
                col = requests.get(cu)
                col = col.json()
                for m in col["manifests"]:
                    man = requests.get(m["@id"])
                    man = man.json()
                    try:
                        for c in man["sequences"][0]["canvases"]:
                            # interlude
                            Display_Picture("iiiflogo128.jpg")
                            w = float(man["sequences"][0]["canvases"][0]["width"])
                            f = int(math.ceil(w/1000))
                            srv = c["images"][0]["resource"]["service"]["@id"]
                            # analyzing
                            if os.path.exists('temp.jpg'):
                                os.remove('temp.jpg')
                            wget.download(srv+"/full/128,128/0/default.jpg", 'temp.jpg')
                            image = Image.open('temp.jpg')
                            draw = ImageDraw.Draw(image)
                            draw.text((0,8), 'Analyzing', fill = "GREEN", font = font)
                            OLED.Display_Image(image)
                            uti = srv+"/full/%d,/0/native.jpg" % (int(round(w/f)))
                            print(uti)
                            img = url_to_image(uti)
                            fcs = analyze_images(img)
                            os.remove('temp.jpg')
                            for (x, y, w, h) in fcs:
                                if os.path.exists('temp.jpg'):
                                    os.remove('temp.jpg')
                                wget.download(srv+"/%d,%d,%d,%d/128,128/0/default.jpg" % (x*f,y*f,w*f,h*f), 'temp.jpg')
                                Display_Picture('temp.jpg')
                                OLED.Delay(3000)    
                                os.remove('temp.jpg')
                    except Exception as e:
                        print(e)
                        print("Error with %s" % m["@id"])


    if __name__ == '__main__':
        main()

except:
    print("\r\nEnd")
    if os.path.exists('temp.jpg'):
        os.remove('temp.jpg')
    OLED.Clear_Screen()
    GPIO.cleanup()

