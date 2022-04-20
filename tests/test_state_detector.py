import threading
import time

import pytest
from BDG.model.board_model import Board
from BSP.BufferlessVideoCapture import BufferlessVideoCapture
from BSP.state_detector import StateDetector
from cv2 import cv2
import BDG.utils.json_util as jsutil
from MockVideoCapture import MockVideoCapture
from BSP.state_handler.state_table import get_state_table, get_last_entry, get_current_state, get_led_ids


def test_blackbox_state_detector_with_zcu102():
    """
    Runs the StateDetector with an example video.
    TODO: This test is not working, because the homography matrix is not correct.
    """

    reference = jsutil.from_json(file_path="./resources/ZCU102/reference/ref.json")

    dec = StateDetector(reference=reference, webcam_id=4)

    cap = MockVideoCapture("./resources/ZCU102/zcu102_video.avi", False)
    dec.open_stream(cap)

    dec._detect_current_state()

    current_state = get_current_state()
    led_ids = get_led_ids()
    # Assert LEDs on and off based on the video
    print(current_state)

    assert current_state[current_state["led_id"] == led_ids[0]]["state"] == "off", "LED 0 not detected correctly"
    assert current_state[current_state["led_id"] == led_ids[1]]["state"] == "on", "LED 1 not detected correctly"
    assert current_state[current_state["led_id"] == led_ids[4]]["state"] == "on", "LED 4 not detected correctly"
    assert current_state[current_state["led_id"] == led_ids[5]]["state"] == "on", "LED 5 not detected correctly"
    assert current_state[current_state["led_id"] == led_ids[6]]["state"] == "off", "LED 6 not detected correctly"

    cv2.waitKey(100)


def test_blackbox_state_detector():
    reference = jsutil.from_json(file_path="resources/Pi/pi_test.json")
    with StateDetector(reference=reference, webcam_id=0) as dec:
        dec.open_stream(MockVideoCapture("./resources/Pi/pi_test.mp4", False))

        for i in range(400):
            dec._detect_current_state()

        # if dec.state_table[0].current_state is None or dec.state_table[1].current_state is None:
        #     continue
        led_0 = get_last_entry("LED_Red")
        led_1 = get_last_entry("LED_Green")
        # Assert LEDs on and off based on the video
        if i < 120:
            assert led_0["state"] == "on", "LED 0 not detected correctly"
            assert led_1["state"] == "on", "LED 1 not detected correctly"
        elif 135 < i < 200:
            assert led_0["state"] == "off", "LED 0 not detected correctly"
            assert led_1["state"] == "off", "LED 1 not detected correctly"
        elif 223 < i < 305:
            assert led_0["state"] == "on", "LED 0 not detected correctly"
            assert led_1["state"] == "on", "LED 1 not detected correctly"
        elif 325 < i < 373:
            assert led_0["state"] == "off", "LED 0 not detected correctly"
            assert led_1["state"] == "off", "LED 1 not detected correctly"
        elif 390 < i:
            assert led_0["state"] == "on", "LED 0 not detected correctly"
            assert led_1["state"] == "on", "LED 1 not detected correctly"

    cv2.destroyAllWindows()

