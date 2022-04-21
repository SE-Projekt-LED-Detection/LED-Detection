import cv2
import numpy as np
import matplotlib.pyplot as plt


def mask_over_expose(img):
    """
    This function returns a mask for overexposed values.
    """
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    y_channel = img_yuv[:, :, 0]
    mask = y_channel < 250
    return mask


def get_dominant_color(img):
    """
    This function returns the dominant hue value of an image.
    """
    mask = mask_over_expose(img)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_hsv = img_hsv[mask]
    hist = cv2.calcHist([img_hsv], [0], None, [180], [0, 180])
    dominant_hue = np.argmax(hist)
    return dominant_hue


def plot_hist(img, title: str = None):
    """
    This function plots the histogram of an image.
    """
    mask = mask_over_expose(img)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_hsv = img_hsv[mask]
    hist = cv2.calcHist([img_hsv], [0], None, [180], [0, 180])
    plt.plot(hist)
    plt.xlim([0, 180])
    plt.show()
