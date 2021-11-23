from cv2 import cv2
import numpy as np
import typing
import matplotlib.pyplot as plt

from src.BSP.BoardOrientation import BoardOrientation


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


def homography_by_sift(ref_img, target_img, distance_factor=0.85, display_result=False) -> BoardOrientation:
    """
    Calculates the board orientation based on SIFT with knnMatch
    :param ref_img: The reference image for the calculation
    :param target_img: The target image for the calculation
    :param distance_factor: Influences the max distance of the matches as per Loew's ration test. A higher value means
     more distant matches are also included. The optimal value may differ based on the board and image
    :param display_result: If true the result is plotted
    :return: A BoardOrientation object which contains the homography matrix and the corners
    """
    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(ref_img, None)
    kp2, des2 = sift.detectAndCompute(target_img, None)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m, n in matches:
        if m.distance < distance_factor * n.distance:
            good.append(m)

    homography_matrix = None
    dst = None
    if len(good) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        homography_matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        matches_mask = mask.ravel().tolist()
        h, w, d = ref_img.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]])
        dst = cv2.perspectiveTransform(np.array([pts]), homography_matrix)[0]
        dst[1], dst[3] = dst[3], dst[1]
    else:
        print("Not enough matches are found - {}/{}".format(len(good), 10))
        matches_mask = None

    if display_result:
        draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                       singlePointColor=None,
                       matchesMask=matches_mask,  # draw only inliers
                       flags=2)
        img3 = cv2.drawMatches(ref_img, kp1, target_img, kp2, good, None, **draw_params)
        plt.imshow(img3, 'gray'), plt.show()

    return BoardOrientation(homography_matrix, dst)


def get_led_roi(board_orientation, reference_hw, led_center):
    """
     Returns the LEDs in the target image based on the homography matrix
    :param board_orientation: The orientation of the board in a BoardOrientation object
    :param reference_hw: A tuple with the height and width of the reference board
    :param led_center: A numpy list with the x,y coordinates of the centers of the LEDs
    :return: The LEDs in the target image
    """

    # Calculates the scaling between the reference and the target board
    scale_x = abs(board_orientation.corners[0][0] - board_orientation.corners[2][0]) / reference_hw[0]
    scale_y = abs(board_orientation.corners[0][1] - board_orientation.corners[1][1]) / reference_hw[1]

    # Transforms the center points
    led_center = cv2.perspectiveTransform(np.array([led_center]), board_orientation.homography_matrix)[0]
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






