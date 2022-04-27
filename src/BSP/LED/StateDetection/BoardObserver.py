import collections
from typing import List

import cv2
import time
import numpy as np

from BSP.LED.ColorDetection import DominantColor, Util
from BSP.LED.LedStateDetector import LedStateDetector
from BSP.LED.StateDetection import Brightness


class BoardObserver:

    def __init__(self, board_leds, debug=False):
        self.leds: List[LedStateDetector] = []
        self.debug = debug

        self._brightnesses = collections.deque(maxlen=30)

        for i in range(len(board_leds)):
            led = board_leds[i]
            self.leds.append(LedStateDetector(led.id, led.colors))

    def check(self, frame: np.array, rois: List[np.array], avg_brightness, on_change)-> None:
        """
        Checks if brightness changed substantially in the image. Invalidates the LEDs if necessary and checks
        all LED states.
        A LED that changed it's state will be passed into the on_change function.

        :param frame: the current frame of the camera stream.
        :param rois: all regions of interest for the LEDs in order.
        :param on_change: the function that should be called when a LED has changed it's state.
        :param avg_brightness:
        :return: None.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = avg_brightness

        self._check_invalidation(brightness)

        for i in range(len(self.leds)):
            led = self.leds[i]
            led_img = rois[i]

            if led.detect_change(led_img):
                on_change(led.name, led.is_on, led.color, led.last_state_time)

            if led.is_on is None:
                self._detect_initial_state(led_img, i, led,brightness, on_change)
            else:
                # Debug show LEDs
                if self.debug:
                    cv2.imshow(str(i), led_img)
                    if led.is_on:
                        led_img[:] = (0, 255, 0)
                    else:
                        led_img[:] = (0, 0, 255)

        if self.debug:
            height, width, channels = frame.shape
            if width > 3000:
                frame = cv2.resize(frame, (int(width / 3), int(height / 3)))

            cv2.imshow("Frame", frame)
            cv2.waitKey(10)

    def _check_invalidation(self, brightness: int) -> None:
        """
        Checks if brightness changed substantially in the image, invalidating all LEDs in this case.
        Large brightness shifts could indicate that the lighting conditions changed which could influence
        the LED state detection.

        :param brightness: the new brightness that should be checked
        :return: None
        """
        deviation = 5
        if len(self._brightnesses) > 0:
            avg_brightness = int(sum(self._brightnesses) / len(self._brightnesses))
            if abs(brightness - avg_brightness) > deviation:
                for led in self.leds:
                    led.invalidate()
        self._brightnesses.append(brightness)

    def _detect_initial_state(self, led_img: np.array, idx: int, led: LedStateDetector, board_brightness, on_change,
                              fixed_threshold: int = -1) -> None:
        """
        Tries to determine the given LEDs status by comparing the LEDs brightness with the brightness of the full image.
        Only used to determine the initial state up to the point where the BrightnessComparison of the LED itself works.

        :param led_img: the LEDs roi.
        :param idx: the current Index for this LED in the StateTable.
        :param led: the LED.
        :param board_brightness
        :param on_change: the function that should be called with the current LEDs state.
        :return: None.
        """
        led_on: bool
        if fixed_threshold in range(0, 256):
            led_brightness = Brightness.avg_brightness(led_img)
            led_on = led_brightness > fixed_threshold
        else:
            self._brightnesses.append(board_brightness)
            led_brightness = Brightness.avg_brightness(led_img)
            avg_brightness = int(sum(self._brightnesses) / len(self._brightnesses))
            deviation = np.std(self._brightnesses)
            led_on = led_brightness > avg_brightness + deviation

        if led_on:
            dominant = DominantColor.get_dominant_color(led_img)
            dominant_name = Util.get_closest_color(dominant, led.cmap)
            on_change(led.name, True, dominant_name, time.time())
            if self.debug:
                led_img[:] = (0, 255, 0)
        else:
            on_change(led.name, False, "", time.time())
            if self.debug:
                led_img[:] = (0, 0, 255)


