from enum import Flag
import sys
import os

import cv2

from rdDetectBlock import anonymizeImg

"""
example : 

$ python3 main.py /facture1.jpg /facture2.jpg /facture3.jpg

$ python3 main.py /facture*.jpg

Ecrit toute les image dans un répertoir /resultatV2 
avec l'image original plus l'image anonymisé

"""
if __name__ == '__main__':

    # setting up result path
    RESULT_PATH = './resultatVF/'

    startParam=1

    #Axel si tu peux essayer de regarder, je sais pas comment faire ça en python
    #Genre avec une constante de l'autre côté (et pas qu'on doivent faire descendre la variable à chaque méthode)
    #talkative=False

    #if(sys.argv[1]=="-t"):
    #    startParam=2
    #    talkative=True

    #for sur tous les arguments donnés par la commande
    for i in range(startParam, len(sys.argv)):
        image = cv2.imread(sys.argv[i])
        file_name = os.path.basename(sys.argv[i])[:-4]

        cv2.imwrite(RESULT_PATH + file_name + '_1original_.jpg', image)

        print(type(file_name))

        print(file_name)

        cv2.imwrite(RESULT_PATH + file_name + '_2ano.jpg', anonymizeImg(image))#, talkative

        print("================================================================================")