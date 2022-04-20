import collections
from typing import List

import cv2
import time
import numpy as np

from BSP.LED.ColorDetection import DominantColor, Util
from BSP.LED.StateDetection import Brightness
from BSP.LED import LedStateDetector

deviation = 5


class BoardObserver:

    def __init__(self):
        self.leds: List[LedStateDetector] = []

        self._brightnesses = collections.deque(maxlen=30)

    def check(self, frame: np.array, rois: List[np.array], on_change, *args, **kwargs) -> None:
        """
        Checks if brightness changed substantially in the image. Invalidates the LEDs if necessary and checks
        all LED states.
        A LED that changed it's state will be passed into the on_change function.
        :param frame: the current frame of the camera stream.
        :param rois: all regions of interest for the LEDs in order.
        :param on_change: the function that should be called when a LED has changed it's state.
        :param args: Further arguments for the on_change function.
        :param kwargs: Further keyword arguments for the on_change function.
        :return: None.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = Brightness.avg_brightness(gray_frame)

        if len(self._brightnesses) > 0:
            avg_brightness = int(sum(self._brightnesses) / len(self._brightnesses))

            if abs(brightness - avg_brightness) > deviation:
                for led in self.leds:
                    led.invalidate()

        self._brightnesses.append(brightness)



        for led in self.leds:
            led_img = rois[led.id]
            if led.detect_change(led_img):
                on_change(led.id, led.name, led.is_on, led.color, led.last_state_time, args, kwargs)
            # Detect initial state
            if led.is_on is None:
                led_brightness = Brightness.avg_brightness(led_img)
                # TODO find a better value for board_brightness
                board_brightness = int(sum(self._brightnesses) / len(self._brightnesses))
                if led_brightness > board_brightness:
                    dominant = DominantColor.get_dominant_color_value(led_img)
                    dominant_name = Util.get_color(dominant)
                    on_change(led.id, led.name, True, dominant_name, time.time(), args, kwargs)
                else:
                    on_change(led.id, led.name, False, "", time.time(), args, kwargs)

        # Debug show LEDs
        resized_frame = cv2.resize(frame, (1632, 1224))
        cv2.imshow("Frame", resized_frame)
        cv2.waitKey(10)
