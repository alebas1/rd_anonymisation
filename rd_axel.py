# regex
import re

# image + ocr
import cv2
import pytesseract

import regex_config

def extract_text_data(image_data):
    text_boxes_arr = []

    # find customer box
    index=0
    for x, b in enumerate(image_data.splitlines()):
        if x != 0:
            b = b.split()
            if len(b) == 12:
                text_boxes_arr.append({
                    'left': int(b[6]),
                    'top': int(b[7]),
                    'width': int(b[8]),
                    'height': int(b[9]),
                    'text': b[11],
                    'index': index
                })
                index+=1

    return text_boxes_arr


def check_regex(text_boxes_arr):
    valid_text_boxes_arr = []
    for t in text_boxes_arr:
        if re.match(regex_config.regex, t['text'], re.IGNORECASE):
            valid_text_boxes_arr.append(t)
    return valid_text_boxes_arr


def anonymize_text(img, ano_boxes, boxes):
    for b in ano_boxes:
        cv2.rectangle(img, (b["left"], b["top"]), (b["left"] + b["width"], b["top"] + b["height"]), (0, 0, 0), -1)

        #looking forward
        i=b["index"]
        while((boxes[i+1]["left"]<=(boxes[i]["left"]+boxes[i]["width"])+20) and (boxes[i+1]["top"]>=boxes[i]["top"]-5 or boxes[i+1]["top"]<=boxes[i]["top"]+5)):
            tmp=boxes[i+1]
            cv2.rectangle(img, (tmp["left"], tmp["top"]), (tmp["left"] + tmp["width"], tmp["top"] + tmp["height"]), (0, 0, 0), -1)
            i+=1

        #looking backward
        i=b["index"]
        while((boxes[i-1]["left"]<=(boxes[i]["left"]+boxes[i]["width"])+20) and (boxes[i+1]["top"]>=boxes[i]["top"]-5 or boxes[i+1]["top"]<=boxes[i]["top"]+5)):
            tmp=boxes[i-1]
            cv2.rectangle(img, (tmp["left"], tmp["top"]), (tmp["left"] + tmp["width"], tmp["top"] + tmp["height"]), (0, 0, 0), -1)
            i-=1

    cv2.imwrite('./image_output.jpg', img)


if __name__ == '__main__':

    #filename = 'factures/midas.jpg'
    filename = 'factures/invoice9.jpg'

    image = cv2.imread(filename)

    # print(pytesseract.image_to_string(image))
    image_data = pytesseract.image_to_data(image)

    # print(extract_text_data(image_data))
    text_data = extract_text_data(image_data)
    for s in text_data:
        print(s)
    valid_ano = check_regex(text_data)
    #for s in valid_ano:
    #    print(s)

    anonymize_text(image, valid_ano, text_data)