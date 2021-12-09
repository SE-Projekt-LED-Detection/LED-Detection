from numbers import Number
import typing
from .util_functions import *



class Led:
    def __init__(self,identifier:str, position: np.array, radius, colors: typing.List[str]):
        """Creates a LED Dataclass

        Args:
            postion (np.array): is a 2D Vector from the Upper Left Corner
                of the Board showing to the center of the led
            radius ([type]): is the radius
        """
        self.id = identifier
        self.position = position
        self.radius = radius
        self.colors = colors


class Board:
    """Defines the position of the Board"""

    def __init__(self, name = "", author= "", img_path="", corners = None, led_objects=[], pil_image = None):
        """inits Board description

        Args:
            name (str): Identifier of the board
            author (str): creator name, can be optional
            img (str): image path for saving image
            corners (np.array): Corner coordinates for the board. Defaults to [].
            led_objects (list, optional): List of all LEDs . Defaults to [].
        """
        self.id = name
        self.author = author
        if corners is not None:
            corners = np.array(corners)
            corners = sort_points(corners)
        self.corners = corners
        self.led = led_objects
        self.img_path = img_path
        if(img_path != ""):
            self.image = cv2.imread(img_path)
        else:
            self.image = pil_image




    def set_board_corners(self, points: typing.List[Number]):
        """creates corner points and sorted them against clockwise direction

        Args:
            points (np.array): is an array of points which are a convex polygon
        """
        points = np.array(points)
        sorted_points = sort_points(points)
        self.corners = sorted_points

    def add_led(self, led: Led, relative_vector=False):
        """Adds an led object and calculates the relative vector if the given vector is from (0,0)
        Args:
            led ([type]): is an led object
            relative_vector (bool, optional): True if the vector is from the upper left corner of the BOARD,
                False if the vector is from the upper left corner of the IMAGE.
                Defaults to False.
        """
        if(not relative_vector):
            led.position = self.get_relative_vector(led.position)

        self.led.append(led)

    def set_image(self, pil_image):
        """sets pil image

        Args:
            pil_image (Image): is an PIL image
        """
        self.image = pil_image

    def get_relative_vector(self, vector: np.array):
        """helper class for calculating relative vector

        Args:
            vector (np.array): [description]

        Returns:
            [type]: [description]
        """
        assert(self.corners is not None)
        assert(self.corners.size > 0)

        # get upper left corner, assert corners are sorted
        ul_corner = self.corners[0]
        relative_vector = ul_corner - vector
        return relative_vector






