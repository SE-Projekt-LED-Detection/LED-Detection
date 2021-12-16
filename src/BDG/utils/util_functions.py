"""
Utility functions for creating Board Description Model such as Sorting Points
"""
import numpy as np
import base64
import pathlib
import cv2


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

    from_center_vectors = center_point - points  # calculating all vectors from center
    index = find_index_closest_point(points, zero_point)
    first_point = from_center_vectors[index]
    momentum = first_point[0] / first_point[1]

    over_180 = np.where(momentum * from_center_vectors[:, 0] - from_center_vectors[:, 1] >= 0, False, True)
    angles = np.apply_along_axis(lambda x: angle_between(x, first_point), 1, from_center_vectors)

    angles[over_180] = 2 * np.pi - angles[over_180]
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
    angle = np.arccos(np.dot(v1_u, v2_u))
    if not np.isnan(angle):
        return angle
    elif np.all(np.equal(v1, v2)):
        return np.pi * 0.0
    else:
        return np.pi



def convert_image_to_data_uri(path: str) -> str:
    '''
    reads an image from path and converts it to a data uri scheme as string

    :param path: is a path to an image
    :return: a binary image as datauri
    '''

    type = pathlib.Path(path).suffix[1:]  # removing dot

    prefix = f"data:image/{type};base64,"

    with open(path, 'rb') as binary_file:
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_message = base64_encoded_data.decode('utf-8')
        datauri = prefix + base64_message
        return datauri


def decode_img_data(img_attr: str) -> np.array:
    """Decodes the embedded image string.

    Args:
        img_attr (str): is the href data
    """

    mime_to_extension = {
        'image/gif': '.gif',
        'image/jpeg': '.jpg',
        'image/png': '.png',
    }
    media_data, data = img_attr.split(',', 1)
    jpg_original = base64.b64decode(data)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=cv2.IMREAD_COLOR)
    cv2.imshow("image", img)
    return img


def led_id_generator(name_prefix= "led-", suffix=0):
    """
    generator function for creating led ids such as led-1
    :param name_prefix:
    :param suffix:
    :return:
    """
    while(True):
        yield name_prefix + str(suffix)
        suffix += 1
