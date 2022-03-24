import cv2
import collections

import Brightness


class BrightnessComparison:
    def __init__(self, deviation: int = 10):
        """
        :param deviation: the deviation of the average on value.
        """
        self._last_brightness = -1
        self._on_values = collections.deque(maxlen=20)
        self._deviation = deviation

    def detect(self, img, window_name: str = None):
        """
        True - LED is powered on.
        False - LED is powered off.
        None - LED is in an undefined state.
        :param img: The BGR image of this LED.
        :param window_name: Set a name, to display a cv2 window with the given img in grayscale.
        :return: True if LED is powered on or None if undefined.
        """
        img = cv2.GaussianBlur(img, (3, 3), 0)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if window_name is not None:
            cv2.imshow(window_name, gray_img)

        # get the average brightness in the given image
        brightness = Brightness.avg_brightness(gray_img)

        # if no known brightness values for on
        if len(self._on_values) == 0:
            if brightness in range(self._last_brightness - self._deviation,
                                   self._last_brightness + self._deviation) or self._last_brightness == -1:
                self._last_brightness = brightness
                return None
            elif brightness > self._last_brightness:
                self._on_values.append(brightness)
                return True
            else:
                self._on_values.append(self._last_brightness)
                return False
        else:
            on_avg = int(sum(self._on_values) / len(self._on_values))
            if brightness in range(on_avg - self._deviation, 256):
                self._on_values.append(brightness)
                return True
            return False

    def invalidate(self) -> None:
        """
        Clears all known brightnesses therefore restarting the state detection.
        :return: None.
        """
        self._on_values.clear()
        self._last_brightness = -1
