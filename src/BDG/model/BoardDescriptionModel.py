from dataclasses import dataclass
from scipy import spatial
import typing
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import cv2 as cv



@dataclass
class Led:
    """structure for led coordinates and """
    position: np.array
    radius: int


@dataclass
class Board:
    """Defines the position of the Board"""


def find_index_closest_point(arr, point):
    """returns closest point using the cartesian product"""
    newList = arr - point
    sort = np.sum(np.power(newList, 2), axis=1)
    return sort.argmin()


def sort_points(points: np.array):
    """
    Sorts a given array of vectors clockwise.
    It is assumed that the spanned polygon is convex

    :param points: is a numpy array of shape n,2 with array[n] = [x_n, y_n].
    :return: the clockwise sorted array
    """

    center_point = np.mean(points, axis=0)

    zero_point = np.zeros(2)

    from_center_vectors = center_point - points# calculating all vectors from center
    index = find_index_closest_point(points, zero_point)
    first_point = from_center_vectors[index]
    momentum = first_point[0]/first_point[1]

    over_180 = np.where(momentum*from_center_vectors[:,0] - from_center_vectors[:,1] > 0, False, True )


    angle = angle_between(from_center_vectors[0], first_point)
    angles = np.apply_along_axis(lambda x: angle_between(x,first_point), 1, from_center_vectors)
    angles[over_180] =2*np.pi - angles[over_180]
    indices = np.argsort(angles)
    return points[indices]




def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.dot(v1_u, v2_u))


if __name__ == '__main__':


    # Create a black image
    img = np.zeros((1000, 1000, 3), np.uint8)
    for i in range(10):
        pts = np.random.random((4,2))
        pts = pts*400
        pts = pts.astype(np.int32)

        images = pts.reshape((-1, 1, 2))
        cv.polylines(img, [images], True, (255,0,0))
        srt_pts = sort_points(pts)
        images = srt_pts.reshape((-1, 1, 2))
        cv.polylines(img, [images], True, (0, 255, 255))
        cv.imshow("image", img)
        print(sort_points(pts))

        # waits for user to press any key
        # (this is necessary to avoid Python kernel form crashing)
        cv.waitKey(0)


    # closing all open windows
    cv.destroyAllWindows()





