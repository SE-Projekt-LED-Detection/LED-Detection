import asyncio
from threading import Thread
from typing import List

from cv2 import cv2
import numpy as np
import sched
import time

from BSP.LED.StateDetection.BoardObserver import BoardObserver
from BSP.LED.LedStateDetector import LedStateDetector
from BDG.model.board_model import Board
from BIP.connection.message.change_msg import BoardChanges
from BIP.connection.mqtt import MQTTConnector
from BIP.connection.mqtt.mqtt_connector import publish_heartbeat
from BSP import led_state_detector
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

    def __init__(self, config: Board, webcam_id: int):
        """
        :param config: The reference which will be used to match features with SIFT
        :param webcam_id: The webcam id which will be used to open a video stream in open_stream()
        """
        self.board = config.get_cropped_board()
        self.webcam_id = webcam_id
        self.delay_in_seconds = 0.05
        self.state_table: List[StateTableEntry] = []
        self.timer: sched.scheduler = sched.scheduler(time.time, time.sleep)
        self.current_orientation: BoardOrientation = None
        self.bufferless_video_capture: BufferlessVideoCapture = None

        self._board_observer = None

        self.create_state_table()

        Thread(target=self.start_mqtt_client).start()

        print("Done")

    def start_mqtt_client(self):
        config = {"broker_address": "89.58.3.45", "broker_port": 1883,
                  "topics": {"changes": "changes", "avail": "avail", "config": "config"}}
        self.mqtt_connector = MQTTConnector(config)
        self.mqtt_connector.connect()

        self.mqtt_connector.loop_start()
        self.mqtt_connector.add_config_handler(lambda client, userdata, message: print(message.payload))
        asyncio.run(publish_heartbeat(self.mqtt_connector))

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
        while True:
            time.sleep(self.delay_in_seconds)
            self._detect_current_state()

    def _detect_current_state(self):
        """
        Detects the current state of the LEDs, updates the StateTable.
        Stream has to be opened with open_stream() before calling this method.
        """
        assert self.bufferless_video_capture is not None, "Video_capture is None. Has the open_stream method been called before?"

        frame = self.bufferless_video_capture.read()

        # frame = cv2.flip(frame, 0)

        if self.current_orientation is None or self.current_orientation.check_if_outdated():
            self.current_orientation = homography_by_sift(self.board.image, frame, display_result=False)

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

    def on_change(self, led: LedStateDetector) -> None:
        """
        Function that should be called when a LED has changed it's state.
        :param led: The LED that changed it's state.
        :return: None.
        """
        entry = self.state_table[led.id]
        new_state = LedState("on" if led.is_on else "off", led.color, led.last_state_time)

        # Calculates the frequency
        if entry.current_state is not None and entry.current_state.power != new_state.power:
            print("Led" + str(led.name) + ": " + new_state.power)

            if new_state.power == "on":
                entry.hertz = 1.0 / (new_state.timestamp - entry.last_time_on)

            self.mqtt_connector.publish_changes(
                BoardChanges(self.board.id, led.name, new_state.power, new_state.color, entry.hertz,
                             new_state.timestamp))

        if new_state.power == "on":
            entry.last_time_on = new_state.timestamp
        else:
            entry.last_time_off = new_state.timestamp

        entry.current_state = new_state
