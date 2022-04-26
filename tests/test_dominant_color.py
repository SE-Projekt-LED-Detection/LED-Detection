import pytest
import numpy as np
import cv2
import matplotlib.pyplot as plt

from BSP.LED.ColorDetection.DominantColor import get_dominant_color, plot_hist


def create_red_img():
    img = np.zeros((100, 100, 3), np.uint8)
    img[:, :, 2] = 255
    return img

def test_get_dominant_color():
    image = create_red_img()
    plt.imshow(image)
    plt.show()
    plot_hist(image)
    color = get_dominant_color(image)
    assert color == 0
