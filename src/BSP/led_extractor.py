from cv2 import cv2
import numpy as np
from typing import List

from src.BDG.model.board_model import Led


def get_led_roi(frame: np.array, leds: List[Led], board_orientation, reference_hw) -> List[np.array]:
    """
     Returns the LEDs in the target image based on the homography matrix
    :param leds: A list with the LED objects which shall be evaluated
    :param frame: The frame where the LEDs will be cut out
    :param board_orientation: The orientation of the board in a BoardOrientation object
    :param reference_hw: A tuple with the height and width of the reference board
    :return: The LEDs in the target image as a list
    """

    # Calculates the scaling between the reference and the target board
    scale_x = abs(board_orientation.corners[0][0] - board_orientation.corners[2][0]) / reference_hw[0]
    scale_y = abs(board_orientation.corners[0][1] - board_orientation.corners[1][1]) / reference_hw[1]

    # Transforms the center points
    led_centers = map(lambda x: x.position, leds)
    led_centers_transformed = cv2.perspectiveTransform(np.array([led_centers]), board_orientation.homography_matrix)[0]
    radius = list(map(lambda led: round(led.radius * max(scale_x, scale_y)), leds))
    leds: List[np.array] = _led_by_circle_coordinates(frame, led_centers_transformed.astype(int), radius)


    # Fills the squares except the circles of the LEDs with gray color
    for led in leds:
        x_coords = np.arange(0, led.shape[0])
        y_coords = np.arange(0, led.shape[1])

        cx = x_coords.size / 2
        cy = y_coords.size / 2
        for x in x_coords:
            for y in y_coords:
                in_circle = (x - cx)**2 + (y-cy)**2 < led.radius**2
                led[x, y] = led[x, y, :] if in_circle else np.array([127, 127, 127])

    return leds


def _led_by_circle_coordinates(frame: np.array, circle_centers: List[np.array], r: List[int]):
    """
    Returns a list of circles with radius r around the center points
    :param circle_centers:
    :param r:
    :return:
    """
    leds = []
    for center in circle_centers:
        top_left = (center[0] - r, center[1] - r)
        bottom_right = (center[0] + r, center[1] + r)
        led = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        leds.append(led)
    return leds
