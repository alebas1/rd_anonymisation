# regex
import re

# image + ocr
import cv2
import pytesseract

import regex_config

def extract_text_data(image_data):
    text_boxes_arr = []

    # find customer box
    for x, b in enumerate(image_data.splitlines()):
        if x != 0:
            b = b.split()
            if len(b) == 12:
                text_boxes_arr.append({
                    'left': int(b[6]),
                    'top': int(b[7]),
                    'width': int(b[8]),
                    'height': int(b[9]),
                    'text': b[11]
                })

    return text_boxes_arr


def check_regex(text_boxes_arr):
    valid_text_boxes_arr = []
    for t in text_boxes_arr:
        if re.match(regex_config.regex, t['text'], re.IGNORECASE):
            valid_text_boxes_arr.append(t)
    return valid_text_boxes_arr


def anonymize_text(img, boxes):
    for b in boxes:
        cv2.rectangle(img, (b["left"], b["top"]), (b["left"] + b["width"], b["top"] + b["height"]), (0, 0, 0), -1)
    cv2.imwrite('./image_output.jpg', img)


if __name__ == '__main__':
    filename = 'factures/midas.jpg'

    image = cv2.imread(filename)

    # print(pytesseract.image_to_string(image))
    image_data = pytesseract.image_to_data(image)

    # print(extract_text_data(image_data))
    valid_ano = check_regex(extract_text_data(image_data))

    anonymize_text(image, valid_ano)