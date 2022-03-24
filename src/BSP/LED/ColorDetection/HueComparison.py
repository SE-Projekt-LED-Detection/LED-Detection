import cv2

from operator import itemgetter

import Util


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
                diff = self._on_histogram
                for i in range(len(self._on_histogram)):
                    diff[i] = self._on_histogram[i, 0] - self._off_histogram[i, 0]
                _, color = self._color(diff)
                return color
        else:
            self._off_histogram = hist

    def _color(self, hist):
        values = []
        for c in self._colors:
            lower, upper = Util.color_range.get(c)
            if lower < 0 < upper:
                values.append((sum(hist[lower:] + hist[0: upper]), c))
            else:
                values.append((sum(hist[lower:upper]), c))
        return max(values, key=itemgetter(0))
