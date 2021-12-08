# regex
import re

# image + ocr
import cv2
import pytesseract

filename = 'image.jpg'

#* read the image and get the dimensions
img = cv2.imread(filename)
hImg, wImg, _ = img.shape

#* get the data from the image
boxes = pytesseract.image_to_data(img)
# print(boxes)

#* create a list of text boxes
text_boxes_arr = []
for x, b in enumerate(boxes.splitlines()):
    if x != 0: # removing the legend line
        b = b.split() # tab separated
        if len(b) == 12: # get boxes with text only
            print(b)
            text_boxes_arr.append(b)
            #* Get the customer box
            if re.compile(r"(customer|client)", re.IGNORECASE).search(b[11]):
                customer_box = b

#* get the boxes on the same line as the customer box
customerline_box_arr = []
for b in text_boxes_arr:
    if b[7] == customer_box[7]:
        customerline_box_arr.append(b)

#* get the box that is the farthest to the right
maxleft_customerline_box = max(map(lambda i: int(i[6]), customerline_box_arr))

#* hide the customer line
cv2.rectangle(img, (int(customer_box[6]), int(customer_box[7])), (int(customer_box[6]) + maxleft_customerline_box, int(customer_box[7]) + int(customer_box[9])), (0, 0, 0), -1)

#* show the output image
cv2.imwrite('./image_output.jpg', img)
print("Image saved to ./image_output.jpg")
