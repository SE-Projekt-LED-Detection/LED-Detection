import collections
from typing import List

import Brightness
import cv2
import numpy as np

from src.BSP.LED import LedStateDetector

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
        avg_brightness = int(sum(self._brightnesses) / len(self._brightnesses))

        if abs(brightness - avg_brightness) > deviation:
            for led in self.leds:
                led.invalidate()

        for led in self.leds:
            gray_roi = cv2.cvtColor(rois[led.id], cv2.COLOR_BGR2GRAY)
            if led.detect(gray_roi):
                on_change(led, args, kwargs)

                # Debug show LEDs
                cv2.imshow(str(led.id), rois[led.id])
                if led.is_on:
                    rois[led.id][:] = (0, 255, 0)
                else:
                    rois[led.id][:] = (0, 0, 255)

        # Debug show LEDs
        cv2.imshow("Frame", frame)

        cv2.waitKey(10)
