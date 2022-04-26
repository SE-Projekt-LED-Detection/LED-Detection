from BSP.LED.ColorDetection.Util import get_closest_color

import cv2


def test_color():
    hue = 117
    color = get_closest_color(hue)
    assert color == "green"


def test_color_2():
    """
    Test if the color is red
    """
    hue = 0
    color = get_closest_color(hue)
    assert color == "red"


def test_green_led_roi():
    roi = cv2.imread("resources/Pi/led_green.png")

