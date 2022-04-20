import cv2

import matplotlib.pyplot as plt
from .image_preprocessing import convert_to_yuv




def get_most_frequent_luminance(img, is_yuv=False):
    """
    Specify the most frequent luminance
    :img: an image in YUV color space
    """
    if is_yuv == False:
        img = convert_to_yuv(img)
    y_channel = img[:, :, 0]
    hist = cv2.calcHist([y_channel], [0], None, [256], [0, 256])
    # ignore black pixels
    return hist[1:].argmax()


def plot_luminance(img, title="ROI Luminance", is_yuv=False):
    """
    Plot the luminance of the image
    :img: an image in YUV color space
    """
    if is_yuv == False:
        img = convert_to_yuv(img)
    y_channel = img[:, :, 0]
    plt.title(title)
    plt.hist(y_channel.ravel(), 256, [0, 256])
    plt.show()


def check_state(roi_img, threshold=0.5):
    """
    Check the state of the LED
    :param roi_img:
    :param threshold:
    :return:
    """
    luminance = get_most_frequent_luminance(roi_img)
    if luminance > threshold:
        return "on"
    else:
        return "off"
