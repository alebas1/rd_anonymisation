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

def searchRegex(regex, strToTest) -> bool:
    regex = regex.replace('i','i*')
    regex = regex.replace('I','I*')
    regex = regex.replace('j','j*')
    regex = regex.replace('J','J*')
    regex = regex.replace('O','O*')
    regex = regex.replace('o','o*')
    regex = regex.replace('ô','ô*')
    regex = regex.replace('é','é*')
    #permet de marquer le char originaux et eviter i -> (i|j) -> (i|(j|i)) 

    regex = regex.replace('i*','(i|j)')
    regex = regex.replace('I*','(I|J)')
    regex = regex.replace('j*','(j|i)')
    regex = regex.replace('J*','(J|I)')
    regex = regex.replace('O*','(O|o|0)')
    regex = regex.replace('o*','(o|O|0)')
    regex = regex.replace('ô*','(ô|o|O|0)')
    regex = regex.replace('é*','(é|e)')
    #print('!!!!!!!!!!!!!!!!!!!!!!!! : ' + regex )
    return re.search(regex,strToTest,re.IGNORECASE)!=None

def anonymize_controleur_block(image,text_data,box):
    i = box['index']+1

    while(not searchRegex('(nom|et|prénom|n|agrément)',text_data[i]['text'])):
        i+=1

    while(not searchRegex('(signature|identification|information)',text_data[i]['text'])):
        draw_anonymizing_rectangle(image,text_data[i])
        i+=1

    return searchRegex('identification|du',text_data[i]['text'])
    

def anonymize_client_block(image,text_data,box):
    i = box['index']+1

    while(not searchRegex('(nom|prénom|raison|sociale)',text_data[i]['text'])):
        i+=1

    while(not searchRegex('résultat',text_data[i]['text'])):
        draw_anonymizing_rectangle(image,text_data[i])
        i+=1

def anonymize_text(image,text_data):
    img=image.copy()
    for b in text_data:
        if searchRegex('(contrôleur|identité)',b['text']):
            if anonymize_controleur_block(img   ,text_data,b): #si return true, alors la facture date d'apres 2018 et n'a pas besoin de traitement suplémentaire
                break   
        if searchRegex('titulaire',b['text']):
            anonymize_client_block(img,text_data,b)
    return img


def anonymize_list(list_ano,img):
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

    #valid_ano = check_regex(text_data, image)

    # for s in text_data:
    #        print(s)

    cv2.imwrite(RESULT_PATH  + file_name + '_2ano.jpg', anonymize_text(image,text_data))

if __name__ == '__main__':

    # setting up result path
    RESULT_PATH = './resultatCT/'

    for i in range(1,len(sys.argv)):

        image = cv2.imread(sys.argv[i])
        file_name = os.path.basename(sys.argv[i])[:-4]

        print(file_name)

        generateImg(image, file_name)

        print("================================================================================")
