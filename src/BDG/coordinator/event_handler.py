from src.BDG.model.board_model import Board
from src.BDG.coordinator.file_handler import FileHandler
from src.BDG.coordinator.edit_handler import EditHandler
import itertools


class EventHandler:
    def __init__(self):
        self.board = Board()
        self.on_update = {
            "on_update_point": [],
            "on_update_image": []

        }

        self.file_handler = FileHandler(self)
        self.edit_handler = EditHandler(self)

    def update_board(self, board: Board):
        self.board = board
        self.update()

    def update(self, channel=""):
        callables = []
        if channel == "":
            callables = [item for sublist in self.on_update.values() for item in sublist]
        elif channel in self.on_update:
            callables = self.on_update.get(channel)

        for x in callables:
            x()

    def update_points(self):
        # skip if there is no image
        if self.board.image is None:
            return
        for f in self.on_update.get("on_update_point"):
            f()

    def update_image(self):
        for f in self.on_update.get("on_update_image"):
            f()
