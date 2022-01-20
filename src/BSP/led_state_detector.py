import time

from src.BSP.led_state import LedState


def get_state(led_roi, colors):
    state = LedState("on", "red", time.time_ns())

    # TODO: return real values instead of dummy values

    return state
