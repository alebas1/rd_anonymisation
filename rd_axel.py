# regex
import re

# image + ocr
import cv2
import pytesseract



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
    for t in text_boxes_arr:
        if re.search(r'()', t['text']):
            valid_text_boxes_arr.append(t)
    return valid_text_boxes_arr


if __name__ == '__main__':
    filename = 'factures/midas.jpg'

    image = cv2.imread(filename)

    # print(pytesseract.image_to_string(image))
    image_data = pytesseract.image_to_data(image)
    print(image_data)

    print(get_text_data(image_data))