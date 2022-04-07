import asyncio
from queue import Queue
import logging
from threading import Thread
from typing import List

from cv2 import cv2
import numpy as np
import sched
import time

from BSP.LED.StateDetection.BoardObserver import BoardObserver
from BSP.LED.LedStateDetector import LedStateDetector
from BDG.model.board_model import Board
from publisher.connection.message.change_msg import BoardChanges
from publisher.connection.mqtt import MQTTConnector
from publisher.connection.mqtt.mqtt_connector import publish_heartbeat
from BSP.BoardOrientation import BoardOrientation
from BSP.BufferlessVideoCapture import BufferlessVideoCapture
from BSP.DetectionException import DetectionException
from BSP.homographyProvider import homography_by_sift
from BSP.led_extractor import get_led_roi
from BSP.led_state import LedState
from BSP.state_table_entry import StateTableEntry


class StateDetector:
    """
    The State Detector continuously detects the current state of the LEDs, meaning whether they are powered on or off,
    which color and the frequency.
    """

    def __init__(self, **kwargs):
        """
        Expected parameters:
        reference (Board): The reference Board object to match the features
        webcam_id (int): The id of the webcam

        Optional parameters:
        logging_level = "DEFAULT": The logging level
        visualizer = FALSE: Visualise the results with the BIP
        validity_seconds = 300: The time until a new homography matrix is calculated

        """
        self.board = kwargs["reference"].get_cropped_board()
        self.webcam_id = kwargs["webcam_id"]
        self.delay_in_seconds = 0.05
        self.state_table: List[StateTableEntry] = []
        self.timer: sched.scheduler = sched.scheduler(time.time, time.sleep)
        self.current_orientation: BoardOrientation = None
        self.bufferless_video_capture: BufferlessVideoCapture = None

        self._board_observer = None

        self.validity_seconds = 300 if kwargs["validity_seconds"] is None else kwargs["validity_seconds"]

        self._closed = False

        self.create_state_table()

        self.state_queue = Queue()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Closing StateDetector")
        self._closed = True
        if self.bufferless_video_capture is not None:
            self.bufferless_video_capture.close()
        cv2.destroyAllWindows()


    def create_state_table(self):
        """
        Creates the state table and fills it with empty entries.
        """
        for led in self.board.led:
            self.state_table.append(StateTableEntry(led.id, None, 0, 0))

    def start(self):
        """
        Starts the detection. Waits the number of seconds configured in the StateDetector, afterwards
        detects the current state. Repeats itself, blocking.
        """
        while not self._closed:
            time.sleep(self.delay_in_seconds)
            self._detect_current_state()

    def _detect_current_state(self):
        """
        Detects the current state of the LEDs, updates the StateTable.
        Stream has to be opened with open_stream() before calling this method.
        """
        assert self.bufferless_video_capture is not None, "Video_capture is None. Has the open_stream method been called before?"

        frame = self.bufferless_video_capture.read()

        if frame is None:
            return

        frame = cv2.rotate(frame, cv2.ROTATE_180)

        if self.current_orientation is None or self.current_orientation.check_if_outdated():
            self.current_orientation = homography_by_sift(self.board.image, frame, display_result=False, validity_seconds=self.validity_seconds)

        leds_roi = get_led_roi(frame, self.board.led, self.current_orientation)
        for roi in leds_roi:
            if roi.shape[0] <= 0 or roi.shape[1] <= 0:
                self.current_orientation = None
                print("Wrong homography matrix. Retry on next frame...")
                return
                # raise DetectionException("Could not detect ROIs probably because of a wrong homography matrix. (ROI size is 0)")

        assert len(leds_roi) == len(self.board.led), "Not all LEDs have been detected."

        # Initialize BoardObserver and all LEDs
        if self._board_observer is None:
            self._board_observer = BoardObserver()
            for i in range(len(self.board.led)):
                led = self.board.led[i]
                self._board_observer.leds.append(LedStateDetector(i, led.id, led.colors))

        # Check LED states
        self._board_observer.check(frame, leds_roi, self.on_change)

        # Publish frame
        self.state_queue.put({"frame": frame})

    def open_stream(self, video_capture: BufferlessVideoCapture = None):
        """
        Opens the video stream.

        :param video_capture: If not none, this video capture will be used, otherwise one will be created based on the
            webcam id. Can be used for tests to pass a mock video capture.
        """
        if video_capture is not None:
            assert isinstance(video_capture, BufferlessVideoCapture), "The passed video capture argument is not of " \
                                                                      "type BufferlessVideoCapture "
            self.bufferless_video_capture = video_capture
            return

        self.bufferless_video_capture = BufferlessVideoCapture(self.webcam_id)

        if not self.bufferless_video_capture.cap.isOpened():
            raise Exception(f"StateDetector is unable to open VideoCapture with index {self.webcam_id}")

    def on_change(self, id: int, name: str, state: bool, color: str, time, *args, **kwargs) -> None:
        """
        Function that should be called when a LED state change has been detected.
        :param id: The id of the LED used to assign the table slot.
        :param name: The name of the LED for clear debug outputs.
        :param state: True if this LED is currently powered on.
        :param color: The color that has been detected.
        :param time: The time the LED changed it's state.
        :return: None.
        """
        entry = self.state_table[id]
        new_state = LedState("on" if state else "off", color, time)

        # Calculates the frequency
        if entry.current_state is not None and entry.current_state.power != new_state.power:
            print("Led" + str(name) + ": " + new_state.power)

            if new_state.power == "on":
                entry.hertz = 1.0 / (new_state.timestamp - entry.last_time_on)

            board_changes = BoardChanges(self.board.id, name, new_state.power, new_state.color, entry.hertz,
                             new_state.timestamp)
            self.state_queue.put({"changes": board_changes})

        if new_state.power == "on":
            entry.last_time_on = new_state.timestamp
        else:
            entry.last_time_off = new_state.timestamp

        entry.current_state = new_state
