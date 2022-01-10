from __future__ import annotations #for typing

import sys
from typing import Dict
import cv2
import numpy as np
from operator import itemgetter

import pytesseract

from pytesseract.pytesseract import Output
import os
from anonymize_utils import check_word_aligned, check_word_backward, check_word_forward, isAtSameMarginAbove, isAtSameMarginBelow, isNotAtSameMarginAbove, isNotAtSameMarginBelow

import regex_config as regex_config
import re

TALK=False #variable pour afficher ou pas les logs : but de test

def affType(arg):
    print(type(arg))
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

def anonymizeImg(image: np.ndarray) -> np.ndarray:  #, talkative:bool

    #TALK=talkative

    image_data = pytesseract.image_to_data(image)
    text_data = extract_text_data(image_data)
    valid_ano = check_regex(text_data, image)

    # for s in text_data:
    #        print(s)

    return anonymize_text(image.copy(), valid_ano, text_data)

#depuis la data renvoyer par tesseract, on récupère seulement les champs qui nous intéresse
def extract_text_data(image_data:str)->list[dict]:
    text_boxes_arr = []

    index = 0
    for (x, b) in enumerate(image_data.splitlines()):
        if x != 0:
            b = b.split()
            if len(b) == 12:
                text_boxes_arr.append({
                    'index': index,
                    'left': int(b[6]),
                    'top': int(b[7]),
                    'width': int(b[8]),
                    'height': int(b[9]),
                    'text': b[11],
                })
                index += 1

    return text_boxes_arr

"""
depuis la data renvoyer par tesseract, on regarde si le texte colle a des regex d'utilisateur :
    Si il y a Monsieur/madame
    Si il y a une adresse (rue, boulevard, impasse, etc...)
"""
def check_regex(text_boxes_arr: list[dict], img: np.ndarray) -> list[dict]:
    valid_text_boxes_arr = []
    for t in text_boxes_arr:
        if re.search(regex_config.regex, t['text'], re.IGNORECASE) and t['top'] <= img.shape[0] * 0.33:
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
def anonymize_text(img: np.ndarray, ano_boxes:list[dict], boxes:list[dict])-> np.ndarray:
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
            print("|--------------------------------------------------------\npremier mot : " + str(boxes[box_ano['index']]))
        isIn = isInList(lists_ano,box_ano)

        if (isIn):
            if(TALK):
                print("| le mot à déjà été traité : " + str(isIn))
        else:

            lists_ano.append([])

            current_list_ano = lists_ano[len(lists_ano) - 1]

            # looking forward
            index_box_ano = box_ano['index']
            anonymize_forward(boxes, index_box_ano, current_list_ano)

            # looking backward
            index_box_ano = box_ano['index']
            beginOfLine = anonymize_backward(boxes, index_box_ano, current_list_ano)

            anonymize_block_below(img, boxes, beginOfLine, current_list_ano)
            if(TALK):
                print('| ')
            anonymize_block_above(img, boxes, beginOfLine, current_list_ano)

    lists_ano = lists_ano[1:] #pour enlever la première list avec une list de 1 dict vide

    checkBlock(lists_ano)

    anonymize_list(lists_ano, img)

    return img

#return true si la box_to_check se trouve deja dans une des list

def isInList(list_ano:list[list[dict]],box_to_check:dict) -> bool:
    rtn = False
    for l in list_ano:
        rtn = next((item for item in l if item['index'] == box_to_check['index']), False) != False or rtn
        # or rtn permet de garder la valeur à true si elle l'as été une seul fois (évite l'utilisation d'un break)
    return rtn

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


def anonymize_list(lists_ano:list[list[dict]], img: np.ndarray) -> None:
    index_to_print = 0
    if(TALK):
        print()
    for list_boxes in lists_ano:
        index_to_print += 1
        for box in list_boxes:
            if(TALK):
                print("ano : " + str(index_to_print) + " | " + str(box))
            draw_anonymizing_rectangle(img, box)
    pass

def draw_anonymizing_rectangle(img: np.ndarray, box: dict) -> None:
    cv2.rectangle(img, (box['left'], box['top']), (box['left']
                                                   + box['width'], box['top'] + box['height']), (0, 0,
                                                                                                 0), -1)

# recursif : anonymise la ligne d'en dessous si le premier mot est à la même marge que la ligne courante
def anonymize_block_below(img: np.ndarray, boxes:list[dict], beginOfLine:int, lists_ano:list[list[dict]]) -> None:
    if(TALK):
        print('|  begin of line below : ' + str(boxes[beginOfLine]))

    index_current_box = beginOfLine
    while isNotAtSameMarginBelow(boxes[beginOfLine], boxes[index_current_box + 1]):
        if(TALK):
            print('|  |  test below : ' + str(boxes[index_current_box]))

        index_current_box += 1

    if(TALK):
        print('|  |  mot prochaine ligne ? ' + str(boxes[index_current_box + 1]))

    if isAtSameMarginBelow(boxes[beginOfLine], boxes[index_current_box + 1]):
        if(TALK):
            print("|  |  mot valide")

        anonymize_forward(boxes, index_current_box + 1, lists_ano)
        anonymize_block_below(img, boxes, index_current_box + 1, lists_ano)


# recursif : anonymise la ligne d'au dessus si le premier mot est à la même marge que la ligne courante
def anonymize_block_above(img: np.ndarray, boxes:list[dict], beginOfLine:int, lists_ano:list[list[dict]]) -> None:
    if(TALK):
        print('|  begin of line above : ' + str(boxes[beginOfLine]))

    index_current_box = beginOfLine
    while isNotAtSameMarginAbove(boxes[beginOfLine], boxes[index_current_box - 1]) and index_current_box > 1:
        if(TALK):
            print('|  |  test above : ' + str(boxes[index_current_box]))
            
        index_current_box -= 1
    if(TALK):
        print('|  |  mot precedente ligne ? ' + str(boxes[index_current_box - 1]))

    if isAtSameMarginAbove(boxes[beginOfLine], boxes[index_current_box - 1]):
        if(TALK):
            print("|  |  ici")

        anonymize_forward(boxes, index_current_box - 1, lists_ano)
        anonymize_block_above(img, boxes, index_current_box - 1, lists_ano)

# Met dans la liste tous les mots qui sont sur la même ligne et devant le mot index_box. Retourne l'index du dernier mot
def anonymize_forward(boxes:list[dict], index_box: int, lists_ano:list[list[dict]]) -> int:
    rtn = boxes[index_box]['index']
    lists_ano.append(boxes[index_box])
    while check_word_forward(boxes[index_box], boxes[index_box + 1], index_box) \
            and check_word_aligned(boxes[index_box], boxes[index_box + 1], index_box):
        box_next = boxes[index_box + 1]
        lists_ano.append(box_next)
        index_box += 1
        rtn = index_box
    return rtn

# Met dans la liste tous les mots qui sont sur la même ligne et derriere le mot index_box. Retourne l'index du premier mot
def anonymize_backward(boxes:list[dict], index_boxe:int, lists_ano:list[list[dict]]) -> int:
    rtn = boxes[index_boxe]['index']
    while check_word_backward(boxes[index_boxe], boxes[index_boxe - 1], index_boxe) \
            and check_word_aligned(boxes[index_boxe], boxes[index_boxe - 1], index_boxe):
        box_prev = boxes[index_boxe - 1]
        lists_ano.append(box_prev)
        index_boxe -= 1
        rtn = index_boxe
    return rtn
