import collections

import typing
import cv2
import numpy as np

from BDG.utils.util_functions import sort_points, split_to_list



class Led:
    def __init__(self, identifier: str, position: np.array, radius, colors: typing.List[str]):
        """Creates a LED Dataclass

        Args:
            position (np.array): is a 2D Vector from the Upper Left Corner
                of the Board showing to the center of the led
            radius ([type]): is the radius
        """
        self.id = identifier
        self.position = position
        self.radius = radius
        self.colors = colors

    def __eq__(self, other):
        """compare if values are equal to reference

        Args:
            other ([any]): is a other object of same type

        Returns:
            [boolean]: True if all values are the same 
        """
        if type(self) is not type(other):
            return False

        if len(self.colors) != len(other.colors):
            return False
        return collections.Counter(self.colors) == collections.Counter(other.colors) \
               and self.id == other.id \
               and np.all(self.position == other.position) \
               and self.radius == other.radius


class Board:
    """Dataclass for Board Specifications"""

    def __init__(self, name="", author="", img_path="", corners = None, led_objects=None, image=None):
        """inits Board description

        Args:
            name (str): Identifier of the board
            author (str): creator name, can be optional
            img_path (str): image path for saving image
            corners (np.array): Corner coordinates for the board. Defaults to [].
            led_objects (list, optional): List of all LEDs . Defaults to [].
        """
        if led_objects is None:
            led_objects = []
        self.id = name
        self.author = author
        if corners is not None:
            corners = sort_points(corners)
            self. corners = corners
        else:
            self.corners = []
        self.led = led_objects
        if img_path != "":
            self.image = cv2.imread(img_path)
        else:
            self.image = image

    def set_board_corners(self, points: typing.List):
        """Creates corner points and sorted them against clockwise direction

        :param points: (np.array): is an array of points which are a convex polygon
        """
        points = split_to_list(points)
        if len(points) > 1:
            points = sort_points(points)

        self.corners = points

    def add_led(self, led: Led, relative_vector=False):
        """Adds an led object and calculates the relative vector if the given vector is from (0,0)

        :param led: Is an LED object
        :param relative_vector: (bool, optional): True if the vector is from the upper left corner of the BOARD,
                False if the vector is from the upper left corner of the IMAGE.
                Defaults to False.
        """
        if not relative_vector:
            led.position = self.get_relative_vector(led.position)

        self.led.append(led)

    def set_image(self, image):
        """Sets pil image

        :param image: (Image): is an PIL image or a str
        """
        if isinstance(image, str):
            image = cv2.imread(image)
        self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def get_relative_vector(self, vector: np.array):
        """helper class for calculating relative vector

        :param vector: np.array
        :return: vector
        """
        assert (self.corners is not None)
        assert (len(self.corners) > 0)

        # get upper left corner, assert corners are sorted
        ul_corner = self.corners[0]
        relative_vector = ul_corner - vector
        return relative_vector

    def get_cropped_board(self):
        assert self.image is not None and len(self.corners) == 4, "No image or not enough corners"

        min_x = min(self.corners, key=lambda t: t[0])[0]
        max_x = max(self.corners, key=lambda t: t[0])[0]
        min_y = min(self.corners, key=lambda t: t[1])[1]
        max_y = max(self.corners, key=lambda t: t[1])[1]

        led = list(map(lambda x: Led(x.id,[x.position[0] - min_x, x.position[1] - min_y], x.radius, x.colors), self.led))

        new_board = Board(self.id, self.author, "", self.corners, led, self.image[min_y:max_y, min_x:max_x])

        return new_board

    def __eq__(self, other):
        """
        TODO!!
        :param other:
        :return:
        """
        return self.id == other.id and self.image == other.image
