from enum import Flag
import sys
import os

import cv2
import pytesseract

from anoInvoice import generate_image_invoice
from anoControleTechnique import generate_image_CT 
from finalVersion.anonymize_utils import extract_text_data, searchRegex
import finalVersion.regex_config as regex_config

"""
    Retourne le int correspondant à 
    Facture : faux
    Contrôle technique : vrai
"""
def is_CT_or_invoice(image,text_data) -> bool:
    rtn = False
    for t in text_data:
        index_current_box = t['index']
        if searchRegex('contrôle',t['text']) and searchRegex('technique',text_data[index_current_box+1]['text']) and t['top'] <= image.shape[0] * 0.25:
            rtn = True
    return rtn

"""
example : 

$ python3 main.py /facture1.jpg /facture2.jpg /facture3.jpg

$ python3 main.py /facture*.jpg

Ecrit toute les image dans un répertoir /resultatV2 
avec l'image original plus l'image anonymisé

"""
if __name__ == '__main__':

    # setting up result path
    RESULT_PATH = './rdResultat/'

    startParam=1

    #if(sys.argv[1]=="-t"):
    #    startParam=2
    #    talkative=True

    #for sur tous les arguments donnés par la commande
    for i in range(startParam, len(sys.argv)):

        image = cv2.imread(sys.argv[i])
        file_name = os.path.basename(sys.argv[i])[:-4]

        print(file_name)

        cv2.imwrite(RESULT_PATH + file_name + '_1original_.jpg', image)
        
        image_data = pytesseract.image_to_data(image)
        text_data = extract_text_data(image_data)

        if(is_CT_or_invoice(image,text_data)):
            print("CT")
            cv2.imwrite(RESULT_PATH + file_name + '_2ano.jpg', generate_image_CT(image,text_data)[1])
        else : 
            print("facture")
            cv2.imwrite(RESULT_PATH + file_name + '_2ano.jpg', generate_image_invoice(image,text_data)[1])

        print("================================================================================")