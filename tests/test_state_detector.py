from src.BDG.model.board_model import Board
from src.BSP.state_detector import StateDetector
from cv2 import cv2
import src.BDG.utils.json_util as jsutil


def test_blackbox_state_detector():
    reference = jsutil.from_json(file_path="resources/pi_test.json")
    dec = StateDetector(reference, 0)
    dec.open_stream(cv2.VideoCapture("./resources/piOnOff3.mp4"))
    dec._detect_current_state()
    pass

