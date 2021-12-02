
from scipy import spatial
import typing
import numpy as np
import util
import cv2 as cv


class Led:
    def __init__(self, postion: np.array, radius, colors: typing.List[str]):
        """Creates a LED Dataclass

        Args:
            postion (np.array): is a 2D Vector from the Upper Left Corner
                of the Board showing to the center of the led
            radius ([type]): is the radius
        """
        self.position = postion
        self.radius = radius
        self.colors = colors


class Board:
    """Defines the position of the Board"""

    def __init__(self, name: str, author: str, img: str, corners, led_objects=[], ):
        """inits Board description

        Args:
            name (str): Identifier of the board
            author (str): creator name, can be optional
            img (str): image path for saving image
            corners (np.array): Corner coordinates for the board. Defaults to [].
            led_objects (list, optional): List of all LEDs . Defaults to [].
        """
        self.name = name
        self.author = author
        self.corners = corners
        self.led = led_objects
        self.img = img

    def set_board_corners(self, points: np.array):
        """creates corner points and sorted them against clockwise direction

        Args:
            points (np.array): is an array of points which are a convex polygon
        """
        sorted_points = util.sort_points(points)
        self.corners = sorted_points
    
    def add_led(self, led:Led, relative_vector= False):
        """Adds an led object and calculates the relative vector if the given vector is from (0,0)
        Args:
            led ([type]): is an led object
            relative_vector (bool, optional): True if the vector is from the upper left corner of the BOARD,
                False if the vector is from the upper left corner of the IMAGE.
                Defaults to False.
        """
        if(not relative_vector):
            


    
    def get_relative_vector(self, vector:np.array):
        """helper class for calculating relative vector

        Args:
            vector (np.array): [description]

        Returns:
            [type]: [description]
        """
        assert(self.corners is not None)
        assert(self.corners.size > 0)

        ul_corner = self.corners[0] # get upper left corner, assert corners are sorted
        relative_vector = ul_corner - vector
        return relative_vector





if __name__ == '__main__':

    # Create a black image
    img = np.zeros((1000, 1000, 3), np.uint8)
    for i in range(10):
        pts = np.random.random((4, 2))
        pts = pts*400
        pts = pts.astype(np.int32)

        images = pts.reshape((-1, 1, 2))
        cv.polylines(img, [images], True, (255, 0, 0))
        srt_pts = util.sort_points(pts)
        images = srt_pts.reshape((-1, 1, 2))
        cv.polylines(img, [images], True, (0, 255, 255))
        cv.imshow("image", img)
        print(util.sort_points(pts))

        # waits for user to press any key
        # (this is necessary to avoid Python kernel form crashing)
        cv.waitKey(0)

    # closing all open windows
    cv.destroyAllWindows()
