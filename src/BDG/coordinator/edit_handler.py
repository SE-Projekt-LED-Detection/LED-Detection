import tkinter

from scipy.spatial import distance

import numpy as np

from src.BDG.model.CreationState import CreationState
from src.BDG.model.board_model import Led, Board
from src.BDG.utils.util_functions import is_equal


class EditHandler:
    def __init__(self, parent: "EventHandler") -> None:
        self.parent = parent
        self.scaling = 1.0
        self.current_state = tkinter.IntVar(CreationState.BOARD.value)
        self.active_circle = None
        self.deleted_corners = []
        self.deleted_leds = []

        self.current_state.trace_add('write', self.clean_active_circle)

    def clean_active_circle(self, var, index, mode):
        self.active_circle = None

    def board(self) -> Board:
        return self.parent.board

    def add_corner(self, event):
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

        self.board().corners = corners
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

        circle = self.check_hovered(x, y)
        if circle is not None:
            self.active_circle = circle
            return

        assert (self.board().image.shape[1] >= x >= 0 and self.board().image.shape[0] >= y >= 0), \
            "Coordinates outside image"

        led = Led("", np.array([x, y]), 20, [])
        self.board().add_led(led, True)

        self.parent.update_points()

    def undo(self):
        if self.is_state(CreationState.BOARD):
            corner_to_remove = self.board().corners.pop()
            self.deleted_corners.append(corner_to_remove)
            self.parent.update_points()
        elif self.is_state(CreationState.LED):
            led_to_remove = self.board().led.pop()
            self.deleted_leds.append(led_to_remove)
            self.parent.update_points()

    def redo(self):
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
            #position = [x for x in self.board().corners if is_equal(x, self.active_circle)]
            for corner in self.board().corners:
                if is_equal(corner, self.active_circle):
                    corner[:] = np.array([x, y])
        if self.is_state(CreationState.LED):
            #position = [x.position for x in self.board().led if is_equal(x.position, self.active_circle)]
            for led in self.board().led:
                if is_equal(led.position, self.active_circle):
                    led.position = np.array([x, y])

        #if position:
        #    position[0][:] = self.active_circle

        self.active_circle = np.array([x, y])

        self.parent.update_points()



    def on_mousewheel(self, event):
        scroll_amount = 0

        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        if event.num == 5 or event.delta == -120:
            scroll_amount = -1
        if event.num == 4 or event.delta == 120:
            scroll_amount = 1

        circle = self.check_hovered(x, y)

        if circle is not None:
            active_led = circle
            active_led.radius += scroll_amount

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
        return self.current_state.get() == state.value
