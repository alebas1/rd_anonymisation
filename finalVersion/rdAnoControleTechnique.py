from __future__ import annotations #for typing

import sys
from typing import Dict
import cv2
import numpy as np

import pytesseract

from pytesseract.pytesseract import Output
import os

from anonymize_utils import anonymize_list, extract_text_data, isInList, searchRegex

def generate_image_CT(image: np.ndarray) -> np.ndarray: 

    image_data = pytesseract.image_to_data(image)
    text_data = extract_text_data(image_data)

    return anonymize_text(image,text_data)

"""
    algo :
        essaie de trouver le bloc garagiste et propriétaire via la recherche de regex.
        Les contrôle technique étant normalisé, on s'appuie sur leur squelette.

        2 possibilités : 
        Avant 2018 : il y a un encart garagiste et client. Bloc d'apres commence par "information sur la visite ..."
        Apres 2018 : il n'y a plus que l'encart garagiste. Bloc d'apres commence par "identification du véhicule"

        Si le bloc d'apres est celui d'apres 2018. Le traitement s'arrête car l'anonymisation est fini
"""
def anonymize_text(image: np.ndarray, text_data:list[dict])-> np.ndarray:
    cpImg=image.copy()
    #Ajoute une première list avec un dict vide, sinon le dict n'est pas initialisé correctement et on ne peut pas faire le premier check en regardant les bonnes keys
    lists_ano = [
        [
            {
                'index': None,
                'left': None,
                'top': None,
                'width': None,
                'height': None,
                'text': None
            }
        ]
    ]

    for current_box in text_data:

        isIn = isInList(lists_ano,current_box) 

        current_list_ano = lists_ano[len(lists_ano) - 1]

        if(not isIn):
            lists_ano.append([])
            if searchRegex('(contrôleur|identité)', current_box['text']):
                if anonymize_controleur_block(text_data, current_box, current_list_ano): #si return true, alors la facture date d'apres 2018 et n'a pas besoin de traitement suplémentaire
                    break   
            if searchRegex('titulaire',current_box['text']):
                anonymize_client_block(text_data,current_box,current_list_ano)

    lists_ano = lists_ano[1:]

    anonymize_list(lists_ano,cpImg)

    return cpImg

#anonymize le bloc constructeur en se basant sur les premiers mots du bloc suivant. Retourne vraie si le bloc suivant correspond à apres 2018
def anonymize_controleur_block(text_data:list[dict], box:dict, list_ano:list[dict]) -> bool:
    index_current_box = box['index']+1

    #permet de commencer l'anonymisation au bonne endroit (plus propre)
    while(not searchRegex('(nom|et|prénom|agrément)',text_data[index_current_box]['text'])):
        index_current_box+=1

    while(not searchRegex('(signature|identification|information)',text_data[index_current_box]['text'])):
        list_ano.append(text_data[index_current_box])
        index_current_box+=1

    return searchRegex('identification|du',text_data[index_current_box]['text'])

#anonymize le bloc constructeur en se basant sur les premiers mots du bloc suivant.
def anonymize_client_block(text_data:list[dict], box:dict, list_ano:list[dict]) -> bool:
    index_current_box = box['index']+1

    #permet de commencer l'anonymisation au bonne endroit (plus propre)
    while(not searchRegex('(nom|prénom|raison|sociale)',text_data[index_current_box]['text'])):
        index_current_box+=1

    while(not searchRegex('résultat',text_data[index_current_box]['text'])):
        list_ano.append(text_data[index_current_box])
        index_current_box+=1


if __name__ == '__main__':

    # setting up result path
    RESULT_PATH = './resultatCT/'

    for i in range(1,len(sys.argv)):

        image = cv2.imread(sys.argv[i])
        file_name = os.path.basename(sys.argv[i])[:-4]

        # rewriting original image
        cv2.imwrite(RESULT_PATH  + file_name + '_1original_.jpg', image)

        print(file_name)

        #generateImg(image, file_name)

        cv2.imwrite(RESULT_PATH + file_name + '_2ano.jpg', generate_image_CT(image))

        print("================================================================================")
