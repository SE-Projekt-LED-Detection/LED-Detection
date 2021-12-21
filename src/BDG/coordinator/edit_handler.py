import tkinter

from scipy.spatial import distance

import src.BDG.utils.json_util as js_util
import numpy as np

from src.BDG.model.CreationState import CreationState
from src.BDG.model.board_model import Led, Board


class EditHandler:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.scaling = 1.0
        self.current_state = tkinter.IntVar()
        self.active_circle = None

    def board(self) -> Board:
        return self.parent.board

    def add_corner(self, event):
        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        circles = self.check_hovered(x, y)
        if circles:
            self.active_circle = circles[0]
            return

        if self.board().corners is None:
            return

        corners = self.board().corners



        assert(self.board().image.shape[1] >= x >= 0 and self.board().image.shape[0] >= y >= 0),\
            "Coordinates outside image"
        assert(len(corners) < 4), "Only 4 corners are possible"


        corners.append([x, y])
        self.parent.update_points()

    def delete_point(self, event):
        """
        Remove a point or a LED
        :param event: is a Mouse event
        :return:
        """
        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        circles = self.check_hovered(x, y)
        if circles[0] is not None:
            if self.is_state(CreationState.BOARD):
                self.board().corners.remove(circles[0])

            if self.is_state(CreationState.LED):
                self.board().led.remove(circles[0])

            self.parent.update_points()

    def add_led(self, event):
        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        circles = self.check_hovered(x, y)
        if circles:
            self.active_circle = circles[0]
            return



        assert (self.board().image.shape[1] >= x >= 0 and self.board().image.shape[0] >= y >= 0),\
            "Coordinates outside image"

        led = Led("", np.array([x, y]), 20, [])
        self.board().add_led(led, True)

        self.parent.update_points()

    def moving_point(self, event):
        """
        Moves the currently selected anchor point or LED
        :param event:
        """

        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        # Moving outside the image?
        if x > self.board().image.shape[1] or y > self.board().image.shape[0] or x < 0 or y < 0:
            return

        if self.active_circle is None:
            return

        if self.is_state(CreationState.BOARD):
            index = self.board().corners.index(self.active_circle)
            self.board().corners.pop(index)
            self.board().corners.insert(index, [x, y])
            self.active_circle = [x, y]
        if self.is_state(CreationState.LED):
            self.active_circle.position = np.array([x, y])

        self.parent.update_points()

    def on_mousewheel(self, event):
        scroll_amount = 0

        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        if event.num == 5 or event.delta == -120:
            scroll_amount = -1
        if event.num == 4 or event.delta == 120:
            scroll_amount = 1

        circles = self.check_hovered(x, y)

        if circles:
            active_led = circles[0]
            active_led.radius += scroll_amount

        self.parent.update_points()

    def check_hovered(self, cx, cy):
        """
        Helper function for checking the currently hovered anchor point or LED.
        :param cx: The x coordinate to check
        :param cy: The y coordinate to check
        :return:
        """
        circles = []
        if self.is_state(CreationState.BOARD):
            circles = filter(lambda x: distance.euclidean((cx, cy), x) <= round(10 / self.scaling), self.board().corners)
        if self.is_state(CreationState.LED):
            circles = filter(lambda x: distance.euclidean((cx, cy), (x.position[0], x.position[1])) <= round(x.radius / self.scaling), self.board().led)
        return list(circles)

    def is_state(self, state):
        return self.current_state.get() == state.value
