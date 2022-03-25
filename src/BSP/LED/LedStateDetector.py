import time
import colorsys

import cv2

from StateDetection.BrightnessComparison import BrightnessComparison
from ColorDetection.HueComparison import Comparison
from ColorDetection import DominantColor, KMeans, Util


class LedStateDetector:

    def __init__(self, id: int, name: str, colors: [str] = None):
        """
        Bounding box should be (left, top, right, bottom).
        Current LED state can be checked with is_on.
        Current LED color can be checked with color.
        The time since the last state change can be checked using passed_time.
        None is used as an undefined state for color, is_on and passed_time.
        :param id: the identification for this LED.
        :param colors: all colors that should be checked for on this LED.
        """
        self._brightness_comparison = BrightnessComparison()
        self._hue_comparison = Comparison(colors)

        self.id: int = id
        self.name: str = name
        self.is_on = None
        self.passed_time = None
        self.last_state_time = None
        self.color = None

    def detect(self, image, imshow: bool = False):
        """
        Checks if the LED at the to be observed location is powered on in the given image.
        If the LED changed it's state, the color will be checked.
        Returns True if the LED has changed it's state i.e. from on to off.
        :param imshow: If set to True, an image with the given defined bbox will be displayed using cv2.imshow().
        :param image: The BGR image of the board that should be checked.
        :return: True if the led has changed it's state.
        """
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if imshow:
            on = self._brightness_comparison.detect(gray_img, str(self.id) + " Gray")
        else:
            on = self._brightness_comparison.detect(gray_img)

        change = on is not None and (self.is_on is None or on is not self.is_on)
        if change:
            self._state_change(on)
            comparison_name = self._hue_comparison.color_detection(image, on)
            if self.is_on:
                rgb = KMeans.k_means(image)
                hsv = colorsys.rgb_to_hsv(rgb[0] / float(255), rgb[1] / float(255), rgb[2] / float(255))
                k_mean_color_name = Util.get_color(int(hsv[0] * 180))
                dominant = DominantColor.get_dominant_color_value(image)
                dominant_name = Util.get_color(dominant)

                # TODO take all colors into consideration
                self.color = comparison_name
                print(self.id, "KMean", k_mean_color_name)
                print(self.id, "HueComparison", comparison_name)
                print(self.id, "Dominant", dominant_name)
        elif self.is_on is None:
            self._hue_comparison.color_detection(image, self.is_on)
        return change

    def _state_change(self, state: bool) -> None:
        self.is_on = state
        if self._last_state_time is None:
            self._last_state_time = time.time()
        else:
            current = time.time()
            self.passed_time = current - self._last_state_time
            self._last_state_time = current

    def invalidate(self) -> None:
        """
        Invalidates this led to restart the state detection.
        :return: None.
        """
        self._brightness_comparison.invalidate()
