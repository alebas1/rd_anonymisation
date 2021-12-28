import sys
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
                    'left': int(b[6]),
                    'top': int(b[7]),
                    'width': int(b[8]),
                    'height': int(b[9]),
                    'text': b[11],
                })
                index += 1

    return text_boxes_arr

def anonymize_text(img, ano_boxes, boxes):
    for b in ano_boxes:
        print("premier mot : "+ str(boxes[b['index']]))
        cv2.rectangle(img, (b['left'], b['top']), (b['left'] + b['width'
                      ], b['top'] + b['height']), (0, 0, 0), -1)
        # looking forward
        i = b['index']

        anonymize_forward(boxes,i,img)

        # looking backward
        beginOfLine=b['index']
        i = b['index']
        while check_word_backward(boxes[i], boxes[i - 1], i) \
            and check_word_aligned(boxes[i], boxes[i - 1], i):
            box_prev = boxes[i - 1]
            draw_anonymizing_rectangle(img, box_prev)
            i -= 1
            beginOfLine=i

        anonymize_block_below(img, boxes, beginOfLine)
        print('|-----------------------')
        anonymize_block_above(img,boxes,beginOfLine)
    return img


#recursive
def anonymize_block_below(img,boxes,beginOfLine):
    print('|  begin of line below : '+str(boxes[beginOfLine]))

    draw_anonymizing_rectangle(img,boxes[beginOfLine])
    anonymize_forward(boxes,beginOfLine,img)
    
    # and boxes[i+1]['top']<=(heightChar+(heightChar/2))*3
    i = beginOfLine
    while isNotAtSameMarginBelow(boxes[beginOfLine],boxes[i+1]):
        print('|  |  test below : '+str(boxes[i]))
        i+=1
    print('|  |  mot prochaine ligne ? '+str(boxes[i+1]))

    #and boxes[i+1]['top']<=img.shape[0]*0.75
    if isAtSameMarginBelow(boxes[beginOfLine],boxes[i+1]): 
        print("|  |  ici")
        anonymize_block_below(img,boxes,i+1)



def anonymize_block_above(img,boxes,beginOfLine):
    print('|  begin of line above : '+str(boxes[beginOfLine]))

    draw_anonymizing_rectangle(img,boxes[beginOfLine])
    anonymize_forward(boxes,beginOfLine,img)

    i = beginOfLine
    while isNotAtSameMarginAbove(boxes[beginOfLine],boxes[i-1]):
        print('|  |  test above : '+str(boxes[i]))
        i-=1
    print('|  |  mot precedente ligne ? '+str(boxes[i-1]))

    if isAtSameMarginAbove(boxes[beginOfLine],boxes[i-1]): 
        print("|  |  ici")
        anonymize_block_above(img,boxes,i-1)



def anonymize_forward(boxes,i,img):
        while check_word_forward(boxes[i], boxes[i + 1], i) \
            and check_word_aligned(boxes[i], boxes[i + 1], i):
            box_next = boxes[i + 1]
            draw_anonymizing_rectangle(img, box_next)
            i += 1

def isNotAtSameMarginBelow(boxe_init, box_curr):
    heightChar=boxe_init['height']
    beginTop=boxe_init['top']
    return (box_curr['left'] <= boxe_init['left']-5 or box_curr['left'] >= boxe_init['left']+5) and box_curr['top']<=beginTop + ((heightChar+(heightChar/2))*3)

def isAtSameMarginBelow(boxe_init, box_curr):
    heightChar=boxe_init['height']
    beginTop=boxe_init['top']
    return box_curr['left'] >= boxe_init['left']-5 and box_curr['left'] <= boxe_init['left']+5 and box_curr['top']<=beginTop + ((heightChar+(heightChar/2))*3)

def isNotAtSameMarginAbove(boxe_init, box_curr):
    heightChar=boxe_init['height']
    beginTop=boxe_init['top']
    return (box_curr['left'] <= boxe_init['left']-5 or box_curr['left'] >= boxe_init['left']+5) and box_curr['top']>=beginTop - ((heightChar+(heightChar/2))*2)

def isAtSameMarginAbove(boxe_init, box_curr):
    heightChar=boxe_init['height']
    beginTop=boxe_init['top']
    return box_curr['left'] >= boxe_init['left']-5 and box_curr['left'] <= boxe_init['left']+5 and box_curr['top']>=beginTop - ((heightChar+(heightChar/2))*2)

def draw_anonymizing_rectangle(img, box):
    cv2.rectangle(img, (box['left'], box['top']), (box['left']
                  + box['width'], box['top'] + box['height']), (0, 0,
                  0), -1)

def check_word_forward(box_curr, box_next, i):
    return box_next['left'] <= box_curr['left'] + box_curr['width'] + 20 \
        and box_next['left'] >= box_curr['left'] + box_curr['width']


def check_word_backward(box_curr, box_prev, i):
    return box_prev['left'] + box_prev['width'] >= box_curr['left'] - 20 \
        and box_prev['left'] + box_prev['width'] <= box_curr['left']


def check_word_aligned(box_curr, box_next, i):
    return box_next['top'] >= box_curr['top'] - 10 and box_next['top'] \
        <= box_curr['top'] + 10

def check_regex(text_boxes_arr, img):
    valid_text_boxes_arr = []
    for t in text_boxes_arr:
        if re.search(regex_config.regex, t['text'], re.IGNORECASE) and t['top']<=img.shape[0]*0.75:
            valid_text_boxes_arr.append(t)
    return valid_text_boxes_arr
    
def generateImg(image, file_name):

    # setting up result path
    RESULT_PATH = './resultatV2/'

    # rewriting original image
    cv2.imwrite(RESULT_PATH  + file_name + '_1original_.jpg', image)

    image_data = pytesseract.image_to_data(image)
    text_data = extract_text_data(image_data)

    valid_ano = check_regex(text_data, image)

    #for s in text_data:
    #        print(s)

    cv2.imwrite(RESULT_PATH  + file_name + '_2ano.jpg', anonymize_text(image.copy(), valid_ano, text_data))

if __name__ == '__main__':

    for i in range(1,len(sys.argv)):

        image = cv2.imread(sys.argv[i])
        file_name = os.path.basename(sys.argv[i])[:-4]

        print(file_name)

        generateImg(image, file_name)

        print("================================================================================")
