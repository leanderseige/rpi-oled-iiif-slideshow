# -*- coding:UTF-8 -*-

import wget
import requests
import urllib.request
import numpy as np
import os
import cv2
import json

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
        minNeighbors=3,
        minSize=(20, 20)
    )
    faceCascadep = cv2.CascadeClassifier("haarcascades/haarcascade_profileface.xml")
    facesp = faceCascadep.detectMultiScale(
        image,
        minNeighbors=3,
        minSize=(20, 20)
    )
    faces=[*facesf,*facesp]
    return faces

#----------------------MAIN-------------------------#

cols = ["https://iiif.manducus.net/collections/0020/collection.json","https://iiif.manducus.net/collections/0019/collection.json","https://iiif.manducus.net/collections/0008/collection.json"]

fn = ""


try:
    def main():
        global fn
        OLED.Device_Init()
        while True:
            for cu in cols:
                col = requests.get(cu)
                col = col.json()
                for m in col["manifests"]:
                    Display_Picture("iiiflogo128.jpg")
                    man = requests.get(m["@id"])
                    man = man.json()
                    srv = man["sequences"][0]["canvases"][0]["images"][0]["resource"]["service"]["@id"]
                    img = url_to_image(srv+"/full/pct:%s,/0/native.jpg"%(4))
                    fcs = analyze_images(img)
                    for (x, y, w, h) in fcs:
                        fn = wget.download(srv+"/%d,%d,%d,%d/128,128/0/default.jpg" % (x*25,y*25,w*25,h*25))
                        Display_Picture(fn)
                        OLED.Delay(3000)    
                        os.remove(fn)


    if __name__ == '__main__':
        main()

except:
    print("\r\nEnd")
    os.remove(fn)
    OLED.Clear_Screen()
    GPIO.cleanup()

