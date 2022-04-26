import time

from BSP.LED.StateDetection.BrightnessComparison import BrightnessComparison
from BSP.LED.ColorDetection.HueComparison import Comparison
from BSP.LED.ColorDetection.Util import create_new_cmap


class LedStateDetector:

    def __init__(self, name: str, colors: [str] = None):
        """
        Current LED state can be checked with is_on.
        Current LED color can be checked with color.
        The time since the last state change can be checked using passed_time.
        None is used as an undefined state for color, is_on and passed_time.
        :param id: the identification for this LED.
        :param: name: the name of this LED for Human readable output.
        :param colors: all colors that should be checked for on this LED.
        """
        self._brightness_comparison = BrightnessComparison()
        self._hue_comparison = Comparison(colors)

        self.name: str = name
        self.is_on = None
        self.last_state_time = None
        self.color: str = ""
        self.cmap = create_new_cmap(colors)

    def detect_change(self, image):
        """
        Checks if the LED in the given image changes it's state.
        If the LED changed it's state, the color will be checked.
        Returns True if the LED has changed it's state i.e. from on to off.

        :param image: The BGR image of the board that should be checked.
        :return: True if the led has changed it's state.
        """
        on = self._brightness_comparison.detect(image)

        change = on is not None and (self.is_on is None or on is not self.is_on)
        if change:
            self._state_change(on, image)
        elif self.is_on is None:
            self._hue_comparison.color_detection(image, self.is_on)
        return change

    def _state_change(self, on: bool, image) -> None:
        """
        Function that is called when the LED changed it's state.

        :param on: True if the LED is on.
        :param image: The roi image of this LED.
        :return: None.
        """
        self.is_on = on
        self.last_state_time = time.time()

        comparison_name = self._hue_comparison.color_detection(image, on)
        if on:
            self.color = comparison_name

    def invalidate(self) -> None:
        """
        Invalidates this led to restart the state detection.

        :return: None.
        """
        self._brightness_comparison.invalidate()
