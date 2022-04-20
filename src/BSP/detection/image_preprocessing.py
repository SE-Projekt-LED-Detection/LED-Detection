import numpy as np
import cv2
import matplotlib.pyplot as plt
from BDG.utils.util_functions import sort_points


def convert_to_yuv(img):
    """
    Convert an RGB image to YUV
    Y = 0.299R + 0.587G + 0.114B and is the luminance
    U = -0.147R - 0.289G + 0.436B and is the blue-difference chrominance
    V = 0.615R - 0.515G - 0.100B and is the red-difference chrominance
    """
    yuv_img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    return yuv_img


def create_mask(contours, width, height):
    """
    creates a black and white mask from the contours
    :param contours:
    :return:
    """
    img = np.zeros((height, width), np.uint8)
    cv2.fillPoly(img, pts=[contours], color=(255, 255, 255))
    return img


def mask_background(frame, contours):
    """
    filters out the background using a mask
    :param frame: is the webcam frame
    :param contours: is the contours of the object
    :return:
    """
    sort_points(contours)
    contours = np.array(contours, dtype=int)
    mask = create_mask(contours, frame.shape[1], frame.shape[0])
    img = cv2.bitwise_and(frame, frame, mask=mask)
    return img



