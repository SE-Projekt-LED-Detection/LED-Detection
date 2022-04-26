import cv2
import numpy as np

from operator import itemgetter

from BSP.LED.ColorDetection.Util import get_closest_color
from BSP.LED import ColorDetection


class Comparison:
    def __init__(self, colors: [str] = None):
        if colors is None:
            colors = []
        self._colors = colors
        self._off_histogram = None
        self._on_histogram = None

    def color_detection(self, frame, is_on) -> str:
        """
        Helper function using a naive attempt at detecting the LED's color by comparing the color changes
        from an off-state and an on-state. The difference in color should be the LED's color.

        :param frame: A BGR frame of the led.
        :param is_on: True if the LED is on. False if LED is off. None if LED state is unknown.
        :return: Name of the color or an empty string for no color.
        """
        if len(self._colors) == 0:
            return ""

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 179])
        # undefined led state
        if is_on is None:
            self._on_histogram = hist
            self._off_histogram = hist
        elif is_on:
            self._on_histogram = hist
            if self._off_histogram is not None:
                diff = self._on_histogram[:, 0] - self._off_histogram[:, 0]
                return self._color(diff)
        else:
            self._off_histogram = hist

    def _color(self, hist: [int]) -> str:
        """
        Calculates the integrals over all assigned colors and their boundaries.

        :param hist: the histogram with flattened shape
        :return: returns the color with the greatest integral
        """
        values = []
        for color in self._colors:
            lower, upper = ColorDetection.COLOR_RANGE.get(color)
            i = integral(hist, lower, upper)
            values.append((i, color))
        return max(values, key=itemgetter(0))[1]


def integral(hist: [int], lower: int, upper: int):
    """
    Returns the integral of the given histogram within the given boundaries.

    :param hist: the histogram
    :param lower: the lower boundary
    :param upper: the upper boundary
    :return: the integral of the given histogram within the given boundaries
    """
    if lower < 0 < upper:
        return sum(hist[lower:] + hist[0: upper])
    else:
        return sum(hist[lower:upper])


def detect_color_from_hist(hist) -> str:
    """
    returns the color which changed the most
    :returns
    """
    values = np.linspace(0, 179, 180)
    counts = hist[:, 0]
    hue = (np.inner(values, counts) / np.sum(counts)) / 2
    c = get_closest_color(int(hue), ColorDetection.COLOR_HUE_MEANS)
    return c
