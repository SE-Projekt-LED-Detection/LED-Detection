import tkinter

from scipy.spatial import distance

import src.BDG.utils.json_util as js_util
import numpy as np

from src.BDG.model.CreationState import CreationState
from src.BDG.model.board_model import Led, Board


class EditHandler:
    """
    Responsible for edit event of the UI such as creating, deleting, undoing, redoing.
    The methods which alter the LEDs or corners always call the update points method. Consequently the UI just has to
    subscribe to the events and update the content accordingly. Realises the Model View Controller pattern.
    """
    def __init__(self, parent: "EventHandler") -> None:
        self.parent = parent
        self.scaling = 1.0
        self.current_state = tkinter.IntVar()
        self.active_circle = None
        self.deleted_corners = []
        self.deleted_leds = []

        self.current_state.trace_add('write', self.clean_active_circle)

    def clean_active_circle(self, var, index, mode):
        self.active_circle = None

    def board(self) -> Board:
        """
        Returns the current board object
        :return: Board
        """
        return self.parent.board

    def add_corner(self, event):
        """
        Adds a corner at the coordinates of the click event
        :param event: The click event with the x and y coordinate
        :return: None
        """
        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        circles = self.check_hovered(x, y)
        if circles:
            self.active_circle = circles[0]
            return

        if self.board().corners is None:
            return

        corners = self.board().corners

        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        assert (self.board().image.shape[1] >= x >= 0 and self.board().image.shape[0] >= y >= 0), \
            "Coordinates outside image"
        assert (len(corners) < 4), "Only 4 corners are possible"


        corners.append([x, y])
        self.parent.update_points()

    def delete_point(self, event):
        """
        Removes the currently hovered point or LED
        :param event: is a Mouse event
        :return:
        """
        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        circles = self.check_hovered(x, y)
        if circles[0] is not None:
            if self.is_state(CreationState.BOARD):
                self.board().corners.remove(circles[0])
                self.deleted_corners.append(circles[0])

            if self.is_state(CreationState.LED):
                self.board().led.remove(circles[0])
                self.deleted_leds.append(circles[0])

            self.parent.update_points()

    def add_led(self, event):
        """
        Adds a LED on the coordinates in the click event.
        :param event: The click event with x and y coordinates
        :return: None
        """
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

    def undo(self):
        """
        Undoes the last LED or Point
        """
        if self.is_state(CreationState.BOARD):
            corner_to_remove = self.board().corners.pop()
            self.deleted_corners.append(corner_to_remove)
            self.parent.update_points()
        elif self.is_state(CreationState.LED):
            led_to_remove = self.board().led.pop()
            self.deleted_leds.append(led_to_remove)
            self.parent.update_points()

    def redo(self):
        """
        Redoes the last deleted, undone point or LED
        """
        if self.is_state(CreationState.BOARD):
            if len(self.deleted_corners) > 1 and len(self.board().corners) < 4:
                self.board().corners.append(self.deleted_corners.pop())
                self.parent.update_points()
        elif self.is_state(CreationState.LED) and len(self.deleted_leds) > 0:
            self.board().led.append(self.deleted_leds.pop())
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
        """
        Processes a mousewheel event. Optimised for Windows and Unix events.
        Does increase/decrease the radius of the active led.
        :param event: The mousewheel event
        """
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
        """
        Checks if the CreationState is currently in 'state'
        :param state: The state to check
        :return: True, if the CreationState is the passed state
        """
        return self.current_state.get() == state.value
