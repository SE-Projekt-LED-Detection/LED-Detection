import tkinter
from types import SimpleNamespace

from scipy.spatial import distance

import numpy as np

from BDG.model.CreationState import CreationState
from BDG.model.board_model import Led, Board
from BDG.utils.util_functions import is_equal


class EditHandler:
    """
    Responsible for edit event of the UI such as creating, deleting, undoing, redoing.
    The methods which alter the LEDs or corners always call the update points method. Consequently the UI just has to
    subscribe to the events and update the content accordingly. Realises the Model View Controller pattern.
    """
    def __init__(self, parent: "EventHandler") -> None:
        self.parent = parent
        self.scaling = 1.0
        self.current_state = tkinter.IntVar(CreationState.BOARD.value)
        self.board_id = tkinter.StringVar()
        self.board_id.trace('w', self.assign_board_id)
        self.active_circle = None
        self.deleted_corners = []
        self.deleted_leds = []

        self.current_state.trace_add('write', self.clean_active_circle)

    def assign_board_id(self, var, index, mode):
        self.parent.board.id = self.board_id.get()

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
        # skip if image is empty
        if self.board().image is None:
            return

        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        circle = self.check_hovered(x, y)
        if circle is not None:
            self.active_circle = circle
            return

        corners = self.board().corners

        assert (self.board().image.shape[1] >= x >= 0 and self.board().image.shape[0] >= y >= 0), \
            "Coordinates outside image"
        assert (len(corners) < 4), "Only 4 corners are possible"

        corners.append([x, y])
        # adds an additional dimension if array is one dimensional

        self.active_circle = np.array([x, y])
        self.board().corners = corners
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
        if circles is not None:
            if self.is_state(CreationState.BOARD):
                self.board().corners.remove(circles)
            if self.is_state(CreationState.LED):
                self.board().led = list(filter(lambda x: x.position[0] != circles[0] and x.position[1] != circles[1], self.board().led))
            self.parent.update_points()

    def add_led(self, event):
        """
        Adds a LED on the coordinates in the click event.
        :param event: The click event with x and y coordinates
        :return: None
        """
        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        circle = self.check_hovered(x, y)
        if circle is not None:
            self.active_circle = circle
            return

        assert (self.board().image.shape[1] >= x >= 0 and self.board().image.shape[0] >= y >= 0), \
            "Coordinates outside image"

        led = Led("", np.array([x, y]), 20, [])
        self.board().add_led(led, True)

        self.active_circle = np.array([x, y])
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
            if len(self.board().led) == 0:
                return

            led_to_remove = self.board().led.pop()
            self.deleted_leds.append(led_to_remove)
            self.parent.update_points()

    def redo(self):
        """
        Redoes the last deleted, undone point or LED
        """
        if self.is_state(CreationState.BOARD):
            if len(self.deleted_corners) > 0 and len(self.board().corners) < 4:
                self.board().corners.append(self.deleted_corners.pop())
                self.parent.update_points()
        elif self.is_state(CreationState.LED) and len(self.deleted_leds) > 0:
            self.board().led.append(self.deleted_leds.pop())
            self.parent.update_points()

    def move_current_led_one_pixel_horizontally(self, amount: int):
        """
        Moves the active led horizontally by the amount

        :param amount: The amount negative means left, positive right
        :return:
        """
        if self.active_circle is None:
            return

        self.moving_point(SimpleNamespace(x=(self.active_circle[0] + amount) * self.scaling, y=self.active_circle[1] * self.scaling))

    def move_current_led_one_pixel_vertically(self, amount: int):
        """
        Moves the active led vertically by the amount

        :param amount: The amount to move, negative means up, positive down
        :return:
        """
        if self.active_circle is None:
            return

        self.moving_point(SimpleNamespace(x=self.active_circle[0] * self.scaling,
                                          y=(self.active_circle[1] + amount) * self.scaling))

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
            for corner in self.board().corners:
                if is_equal(corner, self.active_circle):
                    corner[:] = np.array([x, y])
        if self.is_state(CreationState.LED):
            for led in self.board().led:
                if is_equal(led.position, self.active_circle):
                    led.position = np.array([x, y])

        self.active_circle = np.array([x, y])

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

        circle = self.check_hovered(x, y)

        for led in self.board().led:
            if is_equal(led.position, circle):
                led.radius += scroll_amount

        self.parent.update_points()

    def check_hovered(self, cx, cy):
        """
        Helper function for checking the currently hovered anchor point or LED.
        :param cx: The x coordinate to check
        :param cy: The y coordinate to check
        :return: an np array
        """
        circles = []

        if self.is_state(CreationState.BOARD):
            corners = self.board().corners
            radius = 10
            # corner is type np.array
            circles = filter(lambda x: distance.euclidean((cx, cy), (x[0], x[1])) <= round(
                radius / self.scaling), corners)
            circles = list(circles)

        if self.is_state(CreationState.LED):
            leds = self.board().led
            # led is of type LED
            circles = filter(lambda x: distance.euclidean((cx, cy), (x.position[0], x.position[1])) <= round(
                x.radius / self.scaling), leds)

            circles = [x.position for x in circles]
        return circles[0] if len(circles) > 0 else None

    def is_state(self, state):
        """
        Checks if the CreationState is currently in 'state'
        :param state: The state to check
        :return: True, if the CreationState is the passed state
        """
        return self.current_state.get() == state.value
