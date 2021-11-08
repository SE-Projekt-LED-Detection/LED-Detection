import cv2
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

def get_led_roi(crn_pts_src, crn_pts_dst, reference_rois: list):
    """
    returns the calculated led roi
    :param crn_pts_src:
    :param crn_pts_dst:
    :param reference_rois:
    :return:
    """
    h, status = cv2.findHomography(crn_pts_src, crn_pts_dst)

    (x_scale, y_scale) = calc_scale(crn_pts_src, crn_pts_dst)

    rois_dst = map(lambda x: np.matmul(h,x), reference_rois)
    rois_dst = map(lambda x: scale_point(x,(x_scale,y_scale)), rois_dst)
    return rois_dst






if __name__ == "__main__":
    img = cv2.imread("baseball.png", cv2.IMREAD_COLOR)






