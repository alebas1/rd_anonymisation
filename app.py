# -*- coding: utf-8 -*-

# regex
import re

# image + ocr
import cv2
import pytesseract

import regex_config


def extract_text_data(image_data):
    text_boxes_arr = []

    index = 0
    for (x, b) in enumerate(image_data.splitlines()):
        if x != 0:
            b = b.split()
            if len(b) == 12:
                text_boxes_arr.append({
                    'left': int(b[6]),
                    'top': int(b[7]),
                    'width': int(b[8]),
                    'height': int(b[9]),
                    'text': b[11],
                    'index': index,
                    })
                index += 1

    return text_boxes_arr


def check_regex(text_boxes_arr):
    valid_text_boxes_arr = []
    for t in text_boxes_arr:
        if re.match(regex_config.regex, t['text'], re.IGNORECASE):
            valid_text_boxes_arr.append(t)
    return valid_text_boxes_arr


def anonymize_text(img, ano_boxes, boxes):
    for b in ano_boxes:
        cv2.rectangle(img, (b['left'], b['top']), (b['left'] + b['width'
                      ], b['top'] + b['height']), (0, 0, 0), -1)
        # looking forward
        i = b['index']

        # print("box to anonymise:", b)
        while check_word_forward(boxes[i], boxes[i + 1], i) \
            and check_word_aligned(boxes[i], boxes[i + 1], i):
            box_next = boxes[i + 1]
            draw_anonymizing_rectangle(img, box_next)
            i += 1 
            # print(box_next)
            # print("check_word_forward:", check_word_forward(boxes[i], boxes[i + 1], i))
            # print('check_word_aligned:', check_word_aligned(boxes[i], boxes[i + 1], i))

        # looking backward
        i = b['index']
        while check_word_backward(boxes[i], boxes[i - 1], i) \
            and check_word_aligned(boxes[i], boxes[i - 1], i):
            box_prev = boxes[i - 1]
            draw_anonymizing_rectangle(img, box_prev)
            i -= 1

    cv2.imwrite('./image_output.jpg', img)


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
    return box_next['top'] >= box_curr['top'] - 5 and box_next['top'] \
        <= box_curr['top'] + 5


if __name__ == '__main__':

    filename = 'factures/midas.jpg'

    image = cv2.imread(filename)

    image_data = pytesseract.image_to_data(image)

    text_data = extract_text_data(image_data)

    valid_ano = check_regex(text_data)

    anonymize_text(image, valid_ano, text_data)
