from __future__ import annotations #for typing

import cv2
import numpy as np

import re

def isNotAtSameMarginBelow(boxe_init, box_curr):
    heightChar = boxe_init['height']
    beginTop = boxe_init['top']
    return (box_curr['left'] <= boxe_init['left'] - 5 or box_curr['left'] >= boxe_init['left'] + 5) and box_curr[
        'top'] <= beginTop + ((heightChar * 1.5) * 3)


def isAtSameMarginBelow(boxe_init, box_curr):
    heightChar = boxe_init['height']
    beginTop = boxe_init['top']
    return box_curr['left'] >= boxe_init['left'] - 5 and box_curr['left'] <= boxe_init['left'] + 5 and box_curr[
        'top'] <= beginTop + ((heightChar * 1.5) * 3)


def isNotAtSameMarginAbove(boxe_init, box_curr):
    heightChar = boxe_init['height']
    beginTop = boxe_init['top']
    return (box_curr['left'] <= boxe_init['left'] - 5 or box_curr['left'] >= boxe_init['left'] + 5) and box_curr[
        'top'] >= beginTop - ((heightChar + (heightChar / 2)) * 2)


def isAtSameMarginAbove(boxe_init, box_curr):
    heightChar = boxe_init['height']
    beginTop = boxe_init['top']
    return box_curr['left'] >= boxe_init['left'] - 5 and box_curr['left'] <= boxe_init['left'] + 5 and box_curr[
        'top'] >= beginTop - ((heightChar + (heightChar / 2)) * 2)


def check_word_forward(box_curr, box_next):
    return box_next['left'] <= box_curr['left'] + box_curr['width'] + 30 \
           and box_next['left'] >= box_curr['left'] + box_curr['width']


def check_word_backward(box_curr, box_prev):
    return box_prev['left'] + box_prev['width'] >= box_curr['left'] - 30 \
           and box_prev['left'] + box_prev['width'] <= box_curr['left']


def check_word_aligned(box_curr, box_next):
    return box_next['top'] >= box_curr['top'] - 10 and box_next['top'] \
           <= box_curr['top'] + 10

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

def draw_anonymizing_rectangle(img: np.ndarray, box: dict) -> None:
    cv2.rectangle(img, (box['left'], box['top']), (box['left']
                                                   + box['width'], box['top'] + box['height']), (0, 0,
                                                                                                 0), -1)

#return true si la box_to_check se trouve deja dans une des list
def isInList(list_ano:list[list[dict]],box_to_check:dict) -> bool:
    rtn = False
    for l in list_ano:
        rtn = next((item for item in l if item['index'] == box_to_check['index']), False) != False or rtn
        # or rtn permet de garder la valeur à true si elle l'as été une seul fois (évite l'utilisation d'un break)
    return rtn

def anonymize_list(lists_ano:list[list[dict]], img: np.ndarray) -> None:
    index_to_print = 0
    for list_boxes in lists_ano:
        index_to_print += 1
        for box in list_boxes:
            draw_anonymizing_rectangle(img, box)
    pass