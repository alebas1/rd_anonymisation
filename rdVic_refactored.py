# -*- coding: utf-8 -*-

# regex
import re

# file
import sys
import os

# image + ocr
import cv2
import pytesseract

import regex_config


# import requests
# from requests.structures import CaseInsensitiveDict


def extract_text_data(image_data):
    text_boxes_arr = []

    index = 0
    for (x, b) in enumerate(image_data.splitlines()):
        if x != 0:
            b = b.split()
            if len(b) == 12:
                text_boxes_arr.append({
                    'index': index,
                    'block_num': int(b[2]),
                    'par_num': int(b[3]),
                    'left': int(b[6]),
                    'top': int(b[7]),
                    'width': int(b[8]),
                    'height': int(b[9]),
                    'text': b[11],
                })
                index += 1

    return text_boxes_arr


def check_regex(text_boxes_arr, regex):
    valid_text_boxes_arr = []
    for t in text_boxes_arr:
        if re.search(regex, t['text'], re.IGNORECASE):
            valid_text_boxes_arr.append(t)
    return valid_text_boxes_arr


def anonymize_text(img, ano_boxes, boxes):
    for b in ano_boxes:
        cv2.rectangle(img, (b['left'], b['top']), (b['left'] + b['width'
        ], b['top'] + b['height']), (0, 0, 0), -1)
        i = b['index']

        while check_word_forward(boxes[i], boxes[i + 1]) \
                and check_word_aligned(boxes[i], boxes[i + 1]):
            box_next = boxes[i + 1]
            draw_ano_rectangle(img, box_next)
            i += 1

        i = b['index']
        while check_word_backward(boxes[i], boxes[i - 1]) \
                and check_word_aligned(boxes[i], boxes[i - 1]):
            box_prev = boxes[i - 1]
            draw_ano_rectangle(img, box_prev)
            i -= 1

    return img


def anonymize_textBlock(img, ano_boxes, boxes):
    for b in ano_boxes:
        cv2.rectangle(img, (b['left'], b['top']), (b['left'] + b['width'
        ], b['top'] + b['height']), (0, 0, 0), -1)
        # looking forward
        b = b['index']

        i = 1
        # print("box to anonymise:", b)
        while check_word_block(boxes[b], boxes[b + i]):
            box_next = boxes[b + i]
            draw_ano_rectangle(img, box_next)
            i += 1

        i = 1
        # looking backward
        while check_word_block(boxes[b], boxes[b - i]):
            box_prev = boxes[b - i]
            draw_ano_rectangle(img, box_prev)
            i += 1

    return img


def anonymize_text_v2(img, ano_boxes, boxes):
    # keep only one word in the list with the same block_num and par_num
    ano_boxes = list({(v['block_num'], v['par_num']): v for v in ano_boxes}.values())

    for b in ano_boxes:
        cv2.rectangle(img, (b['left'], b['top']), (b['left'] + b['width'
        ], b['top'] + b['height']), (0, 0, 0), -1)

        b = b['index']

        # i goes to the index of the first word in the block
        i = find_start_block(boxes, b)

        while check_word_block(boxes[b], boxes[b + i]):
            box_next = boxes[b + i]
            if (re.search(regex_config.regexKepp, box_next['text'], re.IGNORECASE)):
                i = go_end_keeped_data(box_next, boxes)
            else:
                draw_ano_rectangle(img, box_next)

            i += 1

    return img


def go_end_keeped_data(boxe, boxes):
    rtn = boxe['index']
    while check_word_forward(boxe, boxes[rtn + 1]):
        rtn += 1
    return rtn


def find_start_block(boxes, b):
    i = -1
    while check_word_block(boxes[b], boxes[b + i]):
        i -= 1
    i += 1
    return i


def draw_ano_rectangle(img, box):
    cv2.rectangle(img, (box['left'], box['top']), (box['left']
                                                   + box['width'], box['top'] + box['height']), (0, 0,
                                                                                                 0), -1)


def check_word_block(box_curr, box_next):
    return box_next['block_num'] == box_curr['block_num'] and box_next['par_num'] == box_curr['par_num']


def check_word_forward(box_curr, box_next):
    return box_curr['left'] + box_curr['width'] + 20 >= box_next['left'] >= box_curr['left'] + box_curr['width']


def check_word_backward(box_curr, box_prev):
    return box_curr['left'] - 20 <= box_prev['left'] + box_prev['width'] <= box_curr['left']


def check_word_aligned(box_curr, box_next):
    return box_curr['top'] - 5 <= box_next['top'] <= box_curr['top'] + 5


def handle_file_path_args(args):
    if len(args) == 2:
        return args[1]
    return 'factures/midas.jpg'


def get_file_name(file_path):
    return os.path.basename(file_path)


if __name__ == '__main__':
    """
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "multipart/form-data; boundary=ebf9f03029db4c2799ae16b5428b06bd"
    headers["Authorization"] = "8bf54562-3000-11eb-adc1-0242ac120002"

    requests.put('http://localhost:5000/cropdeskew', 
                    headers=headers,
                    data="image=@/home/vroy/Mobivia/Memoracar/rd_anonymisation/factures/invoice1.jpg")
    """

    # get filename in args
    file_path = handle_file_path_args(sys.argv)
    file_name = get_file_name(file_path)
    image = cv2.imread(file_path)

    # setting up result path
    RESULT_PATH = './resultat/'

    # rewriting original image
    cv2.imwrite(RESULT_PATH + '1_original_' + file_name, image)

    image_data = pytesseract.image_to_data(image)
    text_data = extract_text_data(image_data)

    valid_ano = check_regex(text_data, regex_config.regex)
    cv2.imwrite(RESULT_PATH + '2_line_' + file_name, anonymize_text(image.copy(), valid_ano, text_data))
    cv2.imwrite(RESULT_PATH + '3_block_' + file_name, anonymize_textBlock(image.copy(), valid_ano, text_data))
    cv2.imwrite(RESULT_PATH + '4_block_keep_' + file_name, anonymize_text_v2(image.copy(), valid_ano, text_data))
