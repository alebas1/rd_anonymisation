from __future__ import annotations #for typing

from typing import Dict
import numpy as np
from operator import itemgetter

import pytesseract

from anonymize_utils import anonymize_list, extract_text_data, check_word_aligned, check_word_backward, check_word_forward, isAtSameMarginAbove, isAtSameMarginBelow, isInList, isNotAtSameMarginAbove, isNotAtSameMarginBelow, searchRegex
import regex_config as regex_config
import re

TALK=False #variable pour afficher ou pas les logs : but de test

def affType(arg):
    print(type(arg))
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

def generate_image_invoice(image: np.ndarray) -> np.ndarray:  #, talkative:bool

    #TALK=talkative

    image_data = pytesseract.image_to_data(image)
    text_data = extract_text_data(image_data)
    valid_ano = check_regex(text_data, image)

    return anonymize_text(image, valid_ano, text_data)

#depuis la data renvoyer par tesseract, on récupère seulement les champs qui nous intéresse

"""
depuis la data renvoyer par tesseract, on regarde si le texte colle a des regex d'utilisateur :
    Si il y a Monsieur/madame
    Si il y a une adresse (rue, boulevard, impasse, etc...)
"""
def check_regex(text_boxes_arr: list[dict], img: np.ndarray) -> list[dict]:
    valid_text_boxes_arr = []
    for t in text_boxes_arr:
        if searchRegex(regex_config.regex,t['text']) and t['top'] <= img.shape[0] * 0.33:
            valid_text_boxes_arr.append(t)
    return valid_text_boxes_arr

"""
fonction principale de l'algo :
entré :
    img : l'image
    ano_boxes : les mots à anonymiser
    boxes : tous les mots
return :
    l'image avec les mots anonymisés
alog :
    crée une list de list de dict : chaque list de dict sera un des blocs
    boucle sur tous les mots à anonymiser
    vérifie qu'ils ne sont pas dejà dans un des blocs (et sont donc deja traité)
    sinon
    ajoute une nouvelle list (nouveaux bloc)
    il ajoue à la list toute la ligne puis récupère le premier mots de la ligne (pour detecter le bloc)
    ajoute à la list tout le bloc
    trouve le bloc utilisateur et retire les autres des bloc à anonymiser
    anonymise tous les mots dans les blocs finaux
"""
def anonymize_text(image: np.ndarray, ano_boxes:list[dict], text_data:list[dict])-> np.ndarray:

    cpImg = image.copy() 
    
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

    for box_ano in ano_boxes:
        if(TALK):
            print("|--------------------------------------------------------\npremier mot : " + str(text_data[box_ano['index']]))
        isIn = isInList(lists_ano,box_ano)

        if (isIn):
            if(TALK):
                print("| le mot à déjà été traité : " + str(isIn))
        else:

            lists_ano.append([])

            current_list_ano = lists_ano[len(lists_ano) - 1]

            # looking forward
            index_box_ano = box_ano['index']
            anonymize_forward(text_data, index_box_ano, current_list_ano)

            # looking backward
            index_box_ano = box_ano['index']
            beginOfLine = anonymize_backward(text_data, index_box_ano, current_list_ano)

            anonymize_block_below(text_data, beginOfLine, current_list_ano)
            if(TALK):
                print('| ')
            anonymize_block_above(text_data, beginOfLine, current_list_ano)

    lists_ano = lists_ano[1:] #pour enlever la première list avec une list de 1 dict vide

    checkBlock(lists_ano)

    anonymize_list(lists_ano, cpImg)

    return cpImg

#enleve des list la list qui ne sont pas des blocs utilisateur
def checkBlock(lists_ano:list[list[dict]]) -> None:
    index_of_list = 0
    for l in lists_ano:
        lists_ano[index_of_list] = sorted(l, key=itemgetter('index'))
        for b in l:
            if (re.search(regex_config.regexKepp, b['text'], re.IGNORECASE)):
                lists_ano.pop(index_of_list)
                index_of_list-=1
                break
            pass
        index_of_list += 1
    pass

# recursif : anonymise la ligne d'en dessous si le premier mot est à la même marge que la ligne courante
def anonymize_block_below(text_data:list[dict], beginOfLine:int, list_ano:list[dict]) -> None:
    if(TALK):
        print('|  begin of line below : ' + str(text_data[beginOfLine]))

    index_current_box = beginOfLine
    while isNotAtSameMarginBelow(text_data[beginOfLine], text_data[index_current_box + 1]):
        if(TALK):
            print('|  |  test below : ' + str(text_data[index_current_box]))

        index_current_box += 1

    if(TALK):
        print('|  |  mot prochaine ligne ? ' + str(text_data[index_current_box + 1]))

    if isAtSameMarginBelow(text_data[beginOfLine], text_data[index_current_box + 1]):
        if(TALK):
            print("|  |  mot valide")

        anonymize_forward(text_data, index_current_box + 1, list_ano)
        anonymize_block_below(text_data, index_current_box + 1, list_ano)


# recursif : anonymise la ligne d'au dessus si le premier mot est à la même marge que la ligne courante
def anonymize_block_above(text_data:list[dict], beginOfLine:int, list_ano:list[dict]) -> None:
    if(TALK):
        print('|  begin of line above : ' + str(text_data[beginOfLine]))

    index_current_box = beginOfLine
    while isNotAtSameMarginAbove(text_data[beginOfLine], text_data[index_current_box - 1]) and index_current_box > 1:
        if(TALK):
            print('|  |  test above : ' + str(text_data[index_current_box]))
            
        index_current_box -= 1
    if(TALK):
        print('|  |  mot precedente ligne ? ' + str(text_data[index_current_box - 1]))

    if isAtSameMarginAbove(text_data[beginOfLine], text_data[index_current_box - 1]):
        if(TALK):
            print("|  |  ici")

        anonymize_forward(text_data, index_current_box - 1, list_ano)
        anonymize_block_above(text_data, index_current_box - 1, list_ano)

# Met dans la liste tous les mots qui sont sur la même ligne et devant le mot index_box. Retourne l'index du dernier mot
def anonymize_forward(text_data:list[dict], index_box: int, list_ano:list[dict]) -> int:
    rtn = text_data[index_box]['index']
    list_ano.append(text_data[index_box])
    while check_word_forward(text_data[index_box], text_data[index_box + 1]) \
            and check_word_aligned(text_data[index_box], text_data[index_box + 1]):
        box_next = text_data[index_box + 1]
        list_ano.append(box_next)
        index_box += 1
        rtn = index_box
    return rtn

# Met dans la liste tous les mots qui sont sur la même ligne et derriere le mot index_box. Retourne l'index ²du premier mot
def anonymize_backward(text_data:list[dict], index_boxe:int, lists_ano:list[list[dict]]) -> int:
    rtn = text_data[index_boxe]['index']
    while check_word_backward(text_data[index_boxe], text_data[index_boxe - 1]) \
            and check_word_aligned(text_data[index_boxe], text_data[index_boxe - 1]):
        box_prev = text_data[index_boxe - 1]
        lists_ano.append(box_prev)
        index_boxe -= 1
        rtn = index_boxe
    return rtn
