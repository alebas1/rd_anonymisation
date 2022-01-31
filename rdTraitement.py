import sys
import os

import cv2
from cv2 import data, exp

import numpy as np

import matplotlib.pyplot as plt

def treatment(image, seuil):

    rtn = image.copy()

    rtn = cv2.resize(rtn, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    #rtn = cv2.cvtColor(rtn, cv2.COLOR_BGR2GRAY)

    rtn = cv2.threshold(rtn, seuil, 255, cv2.THRESH_BINARY)[1]

    rtn = cv2.bitwise_not(rtn)

    #kernel = np.ones((2, 2), np.uint8)
    #rtn = cv2.dilate(rtn, kernel, iterations=2)

    rtn = cv2.bitwise_not(rtn)

    rtn = cv2.medianBlur(rtn,3)

    rtn = cv2.resize(rtn, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)

    return rtn

def getThreshold(image):
    n,modes,p = plt.hist(image.flatten(), 50, (0, 255))
    x = 12
    t=n[x:-10].argmin() + x
    return modes[t]

if __name__ == '__main__':

    RESULT_PATH = './resulTreat/'
    
    for i in range(1,len(sys.argv)-1):
        image = cv2.imread(sys.argv[i],0)
        file_name = os.path.basename(sys.argv[i])[:-4]

        #print(sys.argv[len(sys.argv)-1])
        
        imgHistEqua = cv2.equalizeHist(image.copy())

        cv2.imwrite(RESULT_PATH  + file_name + '_tested.jpg', image)

        th = getThreshold(imgHistEqua)
        print(th)

        #imageTreat = treatment(image,int(sys.argv[len(sys.argv)-1]))
        imageTreat = treatment(image,th)

        cv2.imwrite(RESULT_PATH  + file_name + 't.jpg', imageTreat)
        cv2.imwrite(RESULT_PATH  + file_name + 'he.jpg', imgHistEqua)