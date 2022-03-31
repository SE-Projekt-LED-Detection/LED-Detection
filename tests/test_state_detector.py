import threading
import time

import pytest
from BDG.model.board_model import Board
from BSP.BufferlessVideoCapture import BufferlessVideoCapture
from BSP.state_detector import StateDetector
from cv2 import cv2
import BDG.utils.json_util as jsutil
from MockVideoCapture import MockVideoCapture


def test_blackbox_state_detector_with_zcu102():
    """
    Runs the StateDetector with an example video.
    """


    reference = jsutil.from_json(file_path="./resources/ZCU102/reference/ref.json")

    dec = StateDetector(reference, 4)

    cap = MockVideoCapture("./resources/ZCU102/zcu102_video.avi", False)
    dec.open_stream(cap)

    dec._detect_current_state()

    assert dec.state_table[0].current_state.power == "off", "LED 0 not detected correctly"
    assert dec.state_table[1].current_state.power == "on", "LED 1 not detected correctly"
    assert dec.state_table[4].current_state.power == "on", "LED 4 not detected correctly"
    assert dec.state_table[5].current_state.power == "on", "LED 5 not detected correctly"
    assert dec.state_table[6].current_state.power == "off", "LED 6 not detected correctly"

    cv2.waitKey(100)


def test_blackbox_state_detector():
    reference = jsutil.from_json(file_path="resources/pi_test.json")
    dec = StateDetector(reference, 0)
    dec.open_stream(MockVideoCapture("./resources/piOnOff2.mp4", False))

    dec._detect_current_state()

    cv2.waitKey(100)

    # TODO: check real values


def run_in_thread(to_run):
    global e
    e = None

    def loop():
        try:
            to_run()
        except Exception as ex:
            global e
            e = ex

    th = threading.Thread(target=loop)
    th.start()

    th.join()

    if e is not None:
        raise e

    assert e is None, "Exception:" + str(e)

