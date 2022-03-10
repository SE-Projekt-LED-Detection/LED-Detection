from cv2 import cv2
import numpy as np
from typing import List

from BDG.model.board_model import Led
from BSP.BoardOrientation import BoardOrientation
from BSP.Rectangle import Rectangle


def get_led_roi(frame: np.array, leds: List[Led], board_orientation: BoardOrientation) -> List[np.array]:
    """
    Returns the LEDs in the target image based on the homography matrix
    Returns the LEDs in the target image based on the homography matrix

    :param leds: A list with the LED objects which shall be evaluated
    :param frame: The frame where the LEDs will be cut out
    :param board_orientation: The orientation of the board in a BoardOrientation object
    :return: The LEDs in the target image as a list
    """

    # Calculates the scaling between the reference and the target board
    scale_x = abs(board_orientation.corners[0][0] - board_orientation.corners[2][0]) / board_orientation.reference_h
    scale_y = abs(board_orientation.corners[0][1] - board_orientation.corners[1][1]) / board_orientation.reference_w

    # Transforms the center points
    led_centers = np.float32(list(map(lambda x: x.position, leds)))
    led_borders = np.float32(list(map(lambda x: [x.position[0] + x.radius, x.position[1] + x.radius], leds)))
    led_centers_transformed = cv2.perspectiveTransform(np.array([led_centers]), board_orientation.homography_matrix)[0]

    led_radius_transformed = cv2.perspectiveTransform(np.array([led_borders]), board_orientation.homography_matrix)[0]

    recs = list(map(lambda center,radius: Rectangle(center[0], center[1], center[0] + radius, center[1] + radius), zip(led_centers_transformed, led_radius_transformed)))

    i = 0
    for rec in recs:
        j = 0
        for other_rec in recs:
            if i == j:
                continue
            if rec & other_rec is not None:
                print("Overlapping")
                break

    radius = []

    for i in range(len(leds)):
        radius.append(round(max(abs(led_centers_transformed[i][0] - led_radius_transformed[i][0]), abs(led_centers_transformed[i][1] - led_radius_transformed[i][1]))))

    #radius = list(map(lambda led: round(led.radius * max(scale_x, scale_y)), leds))
    led_rois: List[np.array] = _led_by_circle_coordinates(frame, led_centers_transformed.astype(int), radius)


    # Fills the squares except the circles of the LEDs with gray color
    for (led, roi) in zip(leds,led_rois):
        x_coords = np.arange(0, roi.shape[0])
        y_coords = np.arange(0, roi.shape[1])

        cx = x_coords.size / 2
        cy = y_coords.size / 2
        for x in x_coords:
            for y in y_coords:
                in_circle = (x - cx)**2 + (y-cy)**2 < led.radius**2
                roi[x, y] = roi[x, y, :] if in_circle else np.array([127, 127, 127])

    return led_rois


def _led_by_circle_coordinates(frame: np.array, circle_centers: List[np.array], r: List[int]):
    """
    Returns a list of circles with radius r around the center points

    :param circle_centers:
    :param r:
    :return:
    """
    leds = []
    for (center, radius) in zip(circle_centers, r):
        top_left = (center[0] - radius, center[1] - radius)
        bottom_right = (center[0] + radius, center[1] + radius)
        led = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        leds.append(led)
    return leds

# https://stackoverflow.com/questions/48477130/find-area-of-overlapping-rectangles-in-python-cv2-with-a-raw-list-of-points
def calculateIntersection(a0, a1, b0, b1):
    if a0 >= b0 and a1 <= b1: # Contained
        return True
    elif a0 < b0 and a1 > b1: # Contains
        return True
    elif a0 < b0 and a1 > b0: # Intersects right
        return True
    elif a1 > b1 and a0 < b1: # Intersects left
        return True
    else: # No intersection (either side)
        return False