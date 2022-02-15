import threading
import time

from src.BDG.model.board_model import Board
from src.BSP.BufferlessVideoCapture import BufferlessVideoCapture
from src.BSP.state_detector import StateDetector
from cv2 import cv2
import src.BDG.utils.json_util as jsutil


def test_blackbox_state_detector_with_zcu102():
    """
    Runs the StateDetector with an example video.
    """

    reference = jsutil.from_json(file_path="./resources/ZCU102/reference/ref.json")

    dec = StateDetector(reference, 4)

    cap = cv2.VideoCapture("./resources/ZCU102/zcu102_video.avi")
    dec.open_stream(cap)

    th = threading.Thread(target=dec.start)
    th.start()

    th.join()

def test_blackbox_state_detector():
    reference = jsutil.from_json(file_path="resources/pi_test.json")
    dec = StateDetector(reference, 0)
    dec.open_stream(BufferlessVideoCapture("./resources/piOnOff2.mp4"))
    th = threading.Thread(target=dec.start)
    th.start()

    th.join()
