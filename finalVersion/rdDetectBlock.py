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

def check_regex(text_boxes_arr, img):
    valid_text_boxes_arr = []
    for t in text_boxes_arr:
        if re.search(regex_config.regex, t['text'], re.IGNORECASE) and t['top'] <= img.shape[0] * 0.33:
            valid_text_boxes_arr.append(t)
    return valid_text_boxes_arr

"""
fonction principake de l'algo :
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
            anonymize_forward(boxes, index_box_ano, img, current_list_ano)

            # looking backward
            index_box_ano = box_ano['index']
            beginOfLine = anonymize_backward(boxes, index_box_ano, img, current_list_ano)

            anonymize_block_below(img, boxes, beginOfLine, current_list_ano)
            if(TALK):
                print('| ')
            anonymize_block_above(img, boxes, beginOfLine, current_list_ano)

    lists_ano = lists_ano[1:] #pour enlever la première list avec une list de 1 dict vide

    print("avant :")
    for l in lists_ano:
        for s in l:
            print("   "+str(s))

    checkBlock(lists_ano)

    print("apres :")
    for l in lists_ano:
        for s in l:
            print("   "+str(s))

    anonymize_list(lists_ano, img)

    return img

"""
return true si la box_to_check se trouve deja dans une des list
"""
def isInList(list_ano:list[list[dict]],box_to_check:dict) -> bool:
    rtn = False
    for l in list_ano:
        rtn = next((item for item in l if item['index'] == box_to_check['index']), False) != False or rtn
        # or rtn permet de garder la valeur à true si elle l'as été une seul fois (évite l'utilisation d'un break)
    return rtn

"""
enleve des list la list qui ne sont pas des blocs utilisateur
"""
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

# recursive
def anonymize_block_below(img, boxes, beginOfLine, lists_ano):
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
            print("|  |  ici")
        anonymize_forward(boxes, index_current_box + 1, img, lists_ano)
        anonymize_block_below(img, boxes, index_current_box + 1, lists_ano)


# recursive
def anonymize_block_above(img, boxes, beginOfLine, list):
    if(TALK):
        print('|  begin of line above : ' + str(boxes[beginOfLine]))

    i = beginOfLine
    while isNotAtSameMarginAbove(boxes[beginOfLine], boxes[i - 1]) and i > 1:
        if(TALK):
            print('|  |  test above : ' + str(boxes[i]))
        i -= 1
    if(TALK):
        print('|  |  mot precedente ligne ? ' + str(boxes[i - 1]))

    if isAtSameMarginAbove(boxes[beginOfLine], boxes[i - 1]):
        if(TALK):
            print("|  |  ici")
        anonymize_forward(boxes, i - 1, img, list)
        anonymize_block_above(img, boxes, i - 1, list)


def anonymize_forward(boxes, i, img, list):
    # draw_anonymizing_rectangle(img, boxes[i])
    list.append(boxes[i])
    while check_word_forward(boxes[i], boxes[i + 1], i) \
            and check_word_aligned(boxes[i], boxes[i + 1], i):
        box_next = boxes[i + 1]
        # draw_anonymizing_rectangle(img, box_next)
        list.append(box_next)
        i += 1


def anonymize_backward(boxes, i:int, img, list):
    rtn = boxes[i]['index']
    while check_word_backward(boxes[i], boxes[i - 1], i) \
            and check_word_aligned(boxes[i], boxes[i - 1], i):
        box_prev = boxes[i - 1]
        # draw_anonymizing_rectangle(img, box_prev)
        list.append(box_prev)
        i -= 1
        rtn = i
    return rtn
