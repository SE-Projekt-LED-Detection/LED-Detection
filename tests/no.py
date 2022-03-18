import threading
import time

from docutils.nodes import reference

from BDG.model.board_model import Board
from BSP.BufferlessVideoCapture import BufferlessVideoCapture
from BSP.led_extractor import get_led_roi
from BSP.state_detector import StateDetector
from cv2 import cv2
import BDG.utils.json_util as jsutil
from BSP.homographyProvider import homography_by_sift
import numpy as np
import os
import pathlib

from MockVideoCapture import MockVideoCapture


def test1():
    path = os.path.dirname(os.path.abspath(__file__))
    reference_path = os.path.join(path, "resources/ZCU102/reference/ref.json")
    print(reference_path)
    reference = jsutil.from_json(file_path=reference_path)

    frame = cv2.imread("/home/cj7/Desktop/leds_near.png")
    current_orientation = homography_by_sift(reference.image, frame, display_result=True)

    h, w = frame.shape[:2]
    un_warped = cv2.warpPerspective(frame, current_orientation.homography_matrix, (w, h), flags=cv2.INTER_LINEAR)
    cv2.imshow("result", un_warped)

    cv2.waitKey(0)
    leds_roi = get_led_roi(frame, reference.led, current_orientation)


    # Debug show LEDs
    i = 0
    for roi in leds_roi:
        cv2.imshow(str(i), np.array(roi))
        roi[:] = (0, 0, 255)
        i += 1

    cv2.imshow("Frame", frame)
    cv2.waitKey(0)

    dec = StateDetector(reference, 0)
    dec.open_stream(BufferlessVideoCapture("/home/cj7/Desktop/test.mov"))
    th = threading.Thread(target=dec.start)
    th.start()

    th.join()


def video_test():
    path = os.path.dirname(os.path.abspath(__file__))
    reference_path = os.path.join(path, "resources/ZCU102/reference/ref.json")
    print(reference_path)
    reference = jsutil.from_json(file_path=reference_path)


    dec = StateDetector(reference, 0)
    dec.open_stream(MockVideoCapture(os.path.join(path, "resources/output.avi"), False))
    th = threading.Thread(target=dec.start)
    th.start()

if __name__ == "__main__":
    video_test()
