from typing import List

from cv2 import cv2
import numpy as np
import sched
import time

from src.BDG.model.board_model import Board
from src.BSP import led_state_detector
from src.BSP.BoardOrientation import BoardOrientation
from src.BSP.BufferlessVideoCapture import BufferlessVideoCapture
from src.BSP.homographyProvider import homography_by_sift
from src.BSP.led_extractor import get_led_roi
from src.BSP.led_state import LedState
from src.BSP.state_table_entry import StateTableEntry


class StateDetector:

    def __init__(self, config: Board, webcam_id: int):
        self.board = config
        self.webcam_id = webcam_id
        self.delay_in_seconds = 1
        self.state_table: List[StateTableEntry] = []
        self.timer: sched.scheduler = sched.scheduler(time.time, time.sleep)
        self.current_orientation: BoardOrientation = None
        self.bufferless_video_capture: BufferlessVideoCapture = None

        self.create_state_table()

    def create_state_table(self):
        for led in self.board.led:
            self.state_table.append(StateTableEntry(led.id, None, 0, 0))

    def start(self):

        while True:
            time.sleep(self.delay_in_seconds)
            self._detect_current_state()

    def _detect_current_state(self):

        assert self.bufferless_video_capture is not None, "Video_capture is None. Has the open_stream been method called before?"

        frame = self.bufferless_video_capture.read()

        if self.current_orientation is None or self.current_orientation.check_if_outdated():
            self.current_orientation = homography_by_sift(self.board.image, frame, display_result=True)

        leds_roi = get_led_roi(frame, self.board.led, self.current_orientation)

        # Debug show LEDs
        i = 0
        for roi in leds_roi:
            cv2.imshow(str(i), roi)
            i += 1

        assert len(leds_roi) == len(self.board.led), "Not all LEDs have been detected."

        led_states: List[LedState] = list(map(lambda x: led_state_detector.get_state(x[0], x[1].colors),
                                              list(zip(leds_roi, self.board.led))))

        for i in range(len(self.state_table)):
            entry = self.state_table[i]
            led = self.board.led[i]
            new_state = led_states[i]
            entry.current_state = new_state

            # Calculates the frequency
            if entry.current_state.power is not new_state.power:
                if new_state.power is "on":
                    entry.hertz = 1.0 / (new_state.timestamp - entry.last_time_off)
                if new_state is "off":
                    entry.hertz = 1.0 / (new_state.timestamp - entry.last_time_on)

            if new_state.power is "on":
                entry.last_time_on = new_state.timestamp
            else:
                entry.last_time_off = new_state.timestamp
        cv2.waitKey(10)

    def open_stream(self, video_capture: BufferlessVideoCapture = None):
        if video_capture is not None:
            assert isinstance(video_capture, BufferlessVideoCapture), "The passed video capture argument is not of " \
                                                                      "type BufferlessVideoCapture "
            self.bufferless_video_capture = video_capture
            return

        self.bufferless_video_capture = BufferlessVideoCapture(self.webcam_id)

        if not self.bufferless_video_capture.parent_video_capture.isOpened():
            raise Exception(f"StateDetector is unable to open VideoCapture with index {self.webcam_id}")
