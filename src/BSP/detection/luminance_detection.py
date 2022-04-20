import cv2

import matplotlib.pyplot as plt

def convert_to_yuv(img):
    """
    Convert an RGB image to YUV
    Y = 0.299R + 0.587G + 0.114B and is the luminance
    U = -0.147R - 0.289G + 0.436B and is the blue-difference chrominance
    V = 0.615R - 0.515G - 0.100B and is the red-difference chrominance
    """
    yuv_img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    return yuv_img

def get_most_frequent_luminance(img, is_yuv=False):
    """
    Specify the most frequent luminance
    :img: an image in YUV color space
    """
    if is_yuv == False:
        img = convert_to_yuv(img)
    y_channel = img[:, :, 0]
    hist = cv2.calcHist([y_channel], [0], None, [256], [0, 256])
    return hist.argmax()

def plot_luminance(img, is_yuv=False):
    """
    Plot the luminance of the image
    :img: an image in YUV color space
    """
    if is_yuv == False:
        img = convert_to_yuv(img)
    y_channel = img[:, :, 0]
    plt.hist(y_channel.ravel(), 256, [0, 256])
    plt.show()
