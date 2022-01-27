import threading
import time

from src.BDG.model.board_model import Board
from src.BSP.BufferlessVideoCapture import BufferlessVideoCapture
from src.BSP.state_detector import StateDetector
from cv2 import cv2
import src.BDG.utils.json_util as jsutil


def test_blackbox_state_detector():
    reference = jsutil.from_json(file_path="resources/pi_test.json")
    dec = StateDetector(reference, 0)
    dec.open_stream(BufferlessVideoCapture("./resources/piOnOff2.mp4"))
    th = threading.Thread(target=dec.start)
    th.start()

    th.join()
