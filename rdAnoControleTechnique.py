import sys
from typing import Dict
import cv2
import numpy as np

import pytesseract

from pytesseract.pytesseract import Output
import os

import regex_config
import re

def extract_text_data(image_data):
    text_boxes_arr = []

    index = 0
    for (x, b) in enumerate(image_data.splitlines()):
        if x != 0:
            b = b.split()
            if len(b) == 12:
                text_boxes_arr.append({
                    'index': index,
                    'block_number': int(b[2]),
                    'left': int(b[6]),
                    'top': int(b[7]),
                    'width': int(b[8]),
                    'height': int(b[9]),
                    'text': b[11],
                })
                index += 1

    return text_boxes_arr


def check_regex(text_boxes_arr, img):
    blocks_to_add = []
    valid_text_boxes_arr = []
    for t in text_boxes_arr:
        if re.search(regex_config.regexControleTechHeaders, t['text'], re.IGNORECASE):
            blocks_to_add.append(t['block_number'])

    for block_number in blocks_to_add:
        for t in text_boxes_arr:
            if t['block_number'] == block_number:
                valid_text_boxes_arr.append(t)    

    return valid_text_boxes_arr


def anonymize_list(list_ano,img):
    print('!!!!!!!!!!!!!!!!!!!list_ano', list_ano)
    i=0
    for b in list_ano: # la premiere list contenant la list avec le dict ou tous les champs sont à None
        i+=1
        draw_anonymizing_rectangle(img, b)
    
    return img

def draw_anonymizing_rectangle(img, box):
    cv2.rectangle(img, (box['left'], box['top']), (box['left']
                  + box['width'], box['top'] + box['height']), (0, 0,
                  0), -1)

def generateImg(image, file_name):

    # rewriting original image
    cv2.imwrite(RESULT_PATH  + file_name + '_1original_.jpg', image)

    image_data = pytesseract.image_to_data(image)
    text_data = extract_text_data(image_data)

    valid_ano = check_regex(text_data, image)

    print('valid_ano', valid_ano)
    # print(image_data)
    #for s in text_data:
    #        print(s)

    cv2.imwrite(RESULT_PATH  + file_name + '_2ano.jpg', anonymize_list(valid_ano, image))

if __name__ == '__main__':

    # setting up result path
    RESULT_PATH = './resultatV2/'

    for i in range(1,len(sys.argv)):

        image = cv2.imread(sys.argv[i])
        file_name = os.path.basename(sys.argv[i])[:-4]

        print(file_name)

        generateImg(image, file_name)

        print("================================================================================")
