from BSP.LED.ColorDetection.HueComparison import *
from BSP.LED.ColorDetection.DominantColor import plot_hist
import cv2


def test_color_detect():
    pass


def test_color_predict():
    hue_comparison = Comparison()

    img = cv2.imread("resources/Pi/led_red.png")
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv_img], [0], None, [180], [0, 179])
    plot_hist(img)

    color = detect_color_from_hist(hist)
    hue_comparison._colors = ["red", "blue", "green", "yellow"]
    expected = hue_comparison._color(hist[:, 0])
    assert color == expected
