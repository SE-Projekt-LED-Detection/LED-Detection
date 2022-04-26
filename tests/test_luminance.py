import pytest
import cv2

# modules to test
from BSP.detection.luminance_detection import get_most_frequent_luminance, plot_luminance


frame = cv2.imread("resources/Pi/pi_test.jpg")
roi = cv2.imread("resources/red_led_roi.png")




def test_luminance():
    plot_luminance(roi, title="ROI")
    plot_luminance(frame, title="Frame")
    most_frequent_luminance = get_most_frequent_luminance(roi)
    assert most_frequent_luminance == 255



