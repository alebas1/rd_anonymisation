import re

import cv2
import pytesseract

filename = 'image.jpg'

# read the image and get the dimensions
img = cv2.imread(filename)
hImg, wImg, _ = img.shape # assumes color image

# run tesseract, returning the bounding boxes
boxes = pytesseract.image_to_data(img) # also include any config options you use

text_boxes_arr = []

# find customer box
for x, b in enumerate(boxes.splitlines()):
    if x != 0:
        b = b.split()
        if len(b) == 12:
            text_boxes_arr.append(b)
            _str = b[11]
            if re.compile(r"(customer|client)", re.IGNORECASE).search(_str):
                customer_box = b

customer_box_left = int(customer_box[6])
customer_box_top = int(customer_box[7])
customer_box_width = int(customer_box[8])
customer_box_height = int(customer_box[9])

sl_box_arr = []
for b in text_boxes_arr:
    if b[7] == customer_box[7]:
        sl_box_arr.append(b)
# show annotated image and wait for keypress

maxbox = max(map(lambda i: int(i[6]), sl_box_arr))
print(maxbox)

cv2.rectangle(img, (customer_box_left, customer_box_top), (customer_box_left + maxbox, customer_box_top + customer_box_height), (0, 0, 0), -1)

cv2.imwrite('./image_output.jpg', img)
# cv2.waitKey(0)