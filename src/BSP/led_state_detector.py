import time

import numpy as np
from cv2 import cv2

from BSP.led_state import LedState


def get_state(led_roi: np.array, colors):

    #led = cv2.cvtColor(led_roi, cv2.COLOR_RGB2HSV)

    mean = np.nanmean(led_roi[..., 2])

    state = LedState("on" if mean > 190 else "off", "red", time.time())

    # TODO: return real values instead of dummy values

    return state
