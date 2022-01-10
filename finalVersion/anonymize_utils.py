import cv2

import regex_config as regex_config
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


def check_word_forward(box_curr, box_next, i):
    return box_next['left'] <= box_curr['left'] + box_curr['width'] + 30 \
           and box_next['left'] >= box_curr['left'] + box_curr['width']


def check_word_backward(box_curr, box_prev, i):
    return box_prev['left'] + box_prev['width'] >= box_curr['left'] - 30 \
           and box_prev['left'] + box_prev['width'] <= box_curr['left']


def check_word_aligned(box_curr, box_next, i):
    return box_next['top'] >= box_curr['top'] - 10 and box_next['top'] \
           <= box_curr['top'] + 10