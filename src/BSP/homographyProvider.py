from cv2 import cv2
import numpy as np
import typing
import matplotlib.pyplot as plt


def calc_scale(crn_pts_src, crn_pts_dst):
    """
    calculates the x scale and y scaling of the image by a set of corner points
    :param crn_pts_src: is a set of corner points of the source image,
     order of them should be LT, RT, LB, RB (L/R= Left/Right, T/B=Top/Botton)
    :param crn_pts_dst: is a set of corner points of the source image,
     order of them should be LT, RT, LB, RB (L/R= Left/Right, T/B=Top/Botton)
    :return: a tuple (scale_x, scale_y)
    """
    dist_src_x = np.linalg.norm(crn_pts_src[0], crn_pts_src[1])
    dist_src_y = np.linalg.norm(crn_pts_src[0], crn_pts_src[3])
    dist_dst_x = np.linalg.norm(crn_pts_dst[0], crn_pts_dst[1])
    dist_dst_y = np.linalg.norm(crn_pts_dst[0], crn_pts_dst[3])

    scale_x = dist_dst_x/dist_src_x
    scale_y = dist_dst_y/dist_src_y

    return (scale_x,scale_y)


def scale_point(point, scaling):
    scaled_point = (point[0]*scaling[0], point[1]*scaling[1])
    return scaled_point


def get_led_roi(homography_matrix, crn_pts, reference_hw, led_center):
    """
        Returns the LEDs in the target image based on the homography matrix
    :param homography_matrix: The homography matrix which translates points from the reference to the target
    :param crn_pts: The calculated corner points of the target board
    :param reference_hw: A tuple with the height and width of the reference board
    :param led_center: A numpy list with the x,y coordinates of the centers of the LEDs
    :return: The LEDs in the target image
    """

    # Calculates the scaling between the reference and the target board
    scale_x = abs(crn_pts[0][0] - crn_pts[2][0]) / reference_hw[0]
    scale_y = abs(crn_pts[0][1] - crn_pts[1][1]) / reference_hw[1]

    # Transforms the center points
    led_center = cv2.perspectiveTransform(np.array([led_center]), homography_matrix)[0]
    radius = round(5 * max(scale_x, scale_y))
    leds = led_by_circle_coordinates(led_center.astype(int), radius)

    # Fills the squares except the circles of the LEDs with gray color
    for led in leds:
        x_coords = np.arange(0, led.shape[0])
        y_coords = np.arange(0, led.shape[1])

        cx = x_coords.size / 2
        cy = y_coords.size / 2
        for x in x_coords:
            for y in y_coords:
                in_circle = (x - cx)**2 + (y-cy)**2 < radius**2
                led[x, y] = led[x, y, :] if in_circle else np.array([127, 127, 127])

    return leds


def led_by_circle_coordinates(circle_centers, r):
    leds = []
    for center in circle_centers:
        top_left = (center[0] - r, center[1] - r)
        bottom_right = (center[0] + r, center[1] + r)
        led = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        leds.append(led)
    return leds





if __name__ == "__main__":
    img = cv2.imread("baseball.png", cv2.IMREAD_COLOR)






