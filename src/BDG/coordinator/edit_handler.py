import src.BDG.utils.json_util as js_util
import numpy as np

from src.BDG.model.board_model import Led


class EditHandler:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.scaling = 1.0

    def board(self):
        return self.parent.board

    def add_corner(self, event):
        if self.board().corners is None:
            return

        corners = self.board().corners

        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        image_shape = self.board().image.shape
        if x > image_shape[0] or y > image_shape[1] or x < 0 or y < 0:
            print("invalid coordinate")
            return

        if len(corners) >= 4:
            print("there are already 4 corners")
            return

        corners.append(np.array([x, y]))
        self.parent.update_points()

    def delete_corner(self, event):
        pass  # TODO

    def add_led(self, event):
        x = round(event.x / self.scaling)
        y = round(event.y / self.scaling)

        image_shape = self.board().image.shape
        if x > image_shape[0] or y > image_shape[1] or x < 0 or y < 0:
            print("invalid coordinate")
            return

        led = Led("", np.array([x, y]), 20, [])
        self.board().add_led(led, True)

        self.parent.update_points()
