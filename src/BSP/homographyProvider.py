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


def homography_by_sift(ref_img, target_img, distance_factor=0.65, display_result=False) -> BoardOrientation:
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

    return BoardOrientation(homography_matrix, dst, ref_img.shape[:2])








