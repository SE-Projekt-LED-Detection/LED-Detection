import asyncio
from logging import debug, error, warning, info
from queue import Queue
import logging
from threading import Thread
from typing import List

import matplotlib.pyplot as plt
from cv2 import cv2
import numpy as np
import sched
import time

from BSP.LED.StateDetection.BoardObserver import BoardObserver
from BSP.LED.LedStateDetector import LedStateDetector
from BDG.model.board_model import Board
from BSP.frame_anotations import frame_anotator
from publisher.connection.message.change_msg import BoardChanges
from publisher.connection.mqtt import MQTTConnector
from publisher.connection.mqtt.mqtt_connector import publish_heartbeat
from BSP.BoardOrientation import BoardOrientation
from BSP.BufferlessVideoCapture import BufferlessVideoCapture
from BSP.DetectionException import DetectionException
from BSP.HomographyProvider import homography_by_sift
from BSP.led_extractor import get_led_roi, get_transformed_borders
from BSP.led_state import LedState
from BSP.state_table_entry import StateTableEntry
from BSP.state_handler.state_table import insert_state_entry


from BSP.detection.image_preprocessing import mask_background
from BSP.detection.luminance_detection import plot_luminance, avg_board_brightness

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
        debug = False: If True shows the windows with the LEDs and the current frame otherwise shows nothing
        """
        self.board = kwargs["reference"].get_cropped_board()
        self.webcam_id = kwargs["webcam_id"]
        self.delay_in_seconds = 0.05
        # self.state_table: List[StateTableEntry] = []
        self.timer: sched.scheduler = sched.scheduler(time.time, time.sleep)
        self.current_orientation: BoardOrientation = None
        self.bufferless_video_capture: BufferlessVideoCapture = None

        self._board_observer = BoardObserver(self.board.led)

        self.validity_seconds = kwargs.get("validity_seconds", 300)
        self.debug = kwargs.get("debug", False)

        self._closed = False

        self.prev_frame_time = time.time()
        self.new_frame_time = time.time()

        self.state_queue = Queue()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Closing StateDetector")
        self._closed = True
        if self.bufferless_video_capture is not None:
            self.bufferless_video_capture.close()
        cv2.destroyAllWindows()


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
            return  # Indicates that video capture is closed and state detector stopped

        frame = cv2.rotate(frame, cv2.ROTATE_180)

        if self.current_orientation is None or self.current_orientation.check_if_outdated():
            self.current_orientation = homography_by_sift(self.board.image, frame, display_result=False,
                                                          validity_seconds=self.validity_seconds)

        masked_frame = mask_background(frame, self.current_orientation.corners)
        #plot_luminance(masked_frame, title="Masked frame")
        avg_brightness = avg_board_brightness(frame, self.current_orientation.corners)

        #plot_luminance(frame, title="Original frame")
        leds_roi = get_led_roi(frame, self.board.led, self.current_orientation)
        for index, roi in enumerate(leds_roi):
            if roi.shape[0] <= 0 or roi.shape[1] <= 0:
                self.current_orientation = None
                warning("One ROI's size is 0. Assuming the homography matrix is wrong, retry on next frame.")
                return


        # Check LED states
        self._board_observer.check(frame, leds_roi,avg_brightness, self.on_change)



        # Publish frame
        leds_borders = get_transformed_borders(self.board.led, self.current_orientation)

        # Calculate FPS
        self.new_frame_time = time.time()
        fps = int(1 / (self.new_frame_time - self.prev_frame_time))
        self.prev_frame_time = self.new_frame_time

        frame_anotator.annotate_frame(frame, leds_borders, fps)
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
            debug("Set video capture to the provided one")
            return

        debug("Opening video capture with device id %s", self.webcam_id)
        self.bufferless_video_capture = BufferlessVideoCapture(self.webcam_id)

        if not self.bufferless_video_capture.cap.isOpened():
            error("The created video capture is not opened.")
            raise Exception(f"StateDetector is unable to open VideoCapture with index {self.webcam_id}.")

    def on_change(self, index: int, name: str, state: bool, color: str, time, *args, **kwargs) -> None:
        """
        Function that should be called when a LED state change has been detected.

        :param index: The index of the LED used to assign the table slot.
        :param name: The name of the LED for clear debug outputs.
        :param state: True if this LED is currently powered on.
        :param color: The color that has been detected.
        :param time: The time the LED changed it's state.
        :return: None.
        """
        state_str = "on" if state else "off"
        entry = insert_state_entry(name, state_str, color, time)

        new_state = LedState("on" if state else "off", color, time)
        board_changes = BoardChanges(self.board.id, name, new_state.power, new_state.color, entry["frequency"],
                                     new_state.timestamp)
        self.state_queue.put({"changes": board_changes})
