import sys
import os

import cv2
from cv2 import data, exp

import numpy as np

def treatment(image):

    rtn = image.copy()

    rtn = cv2.resize(rtn, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    rtn = cv2.cvtColor(rtn, cv2.COLOR_BGR2GRAY)

    rtn = cv2.threshold(rtn, 135, 255, cv2.THRESH_BINARY)[1]

    rtn = cv2.bitwise_not(rtn)

    kernel = np.ones((2, 2), np.uint8)
    rtn = cv2.dilate(rtn, kernel, iterations=2)

    rtn = cv2.bitwise_not(rtn)

    rtn = cv2.medianBlur(rtn,3)

    rtn = cv2.resize(rtn, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)

    return rtn

if __name__ == '__main__':

    RESULT_PATH = './resulTreat/'
    
    for i in range(1,len(sys.argv)):
        image = cv2.imread(sys.argv[i])
        file_name = os.path.basename(sys.argv[i])[:-4]

        cv2.imwrite(RESULT_PATH  + file_name + '_1_original_.jpg', image)
        imageTreat = treatment(image)
        cv2.imwrite(RESULT_PATH  + file_name + '_2_treated_.jpg', imageTreat)