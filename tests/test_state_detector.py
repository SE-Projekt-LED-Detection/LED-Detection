import threading
import time

import pytest
from BDG.model.board_model import Board
from BSP.BufferlessVideoCapture import BufferlessVideoCapture
from BSP.state_detector import StateDetector
from cv2 import cv2
import BDG.utils.json_util as jsutil
from tests.MockVideoCapture import MockVideoCapture


def test_blackbox_state_detector_with_zcu102():
    """
    Runs the StateDetector with an example video.
    """

    try:
        reference = jsutil.from_json(file_path="./resources/ZCU102/reference/ref.json")

        dec = StateDetector(reference, 4)

        cap = MockVideoCapture("./resources/ZCU102/zcu102_video.avi", False)
        dec.open_stream(cap)

        th = threading.Thread(target=dec.start)
        th.start()

        th.join()

    except Exception as e:
        pytest.fail(e)

def test_blackbox_state_detector():
    reference = jsutil.from_json(file_path="resources/pi_test.json")
    dec = StateDetector(reference, 0)
    dec.open_stream(BufferlessVideoCapture("./resources/piOnOff2.mp4"))
    th = threading.Thread(target=dec.start)
    th.start()

    th.join()
