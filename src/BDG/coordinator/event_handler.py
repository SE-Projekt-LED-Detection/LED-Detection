from src.BDG.model.board_model import Board
from src.BDG.coordinator.file_handler import FileHandler
from src.BDG.coordinator.edit_handler import EditHandler



class EventHandler:
    """
    Contains the other event handler and methods to signal an update of the image or the points.
    """
    def __init__(self):
        self.board = Board()
        self.on_update = {
            "on_update_point": [],
            "on_update_image": []

        }

        self.file_handler = FileHandler(self)
        self.edit_handler = EditHandler(self)

    def update_board(self, board: Board):
        """
        Updates the board object in the handler and calls all update methods.
        :param board: The new board which will be set in self
        """
        self.board = board
        self.update()

    def update(self, channel=""):
        """
        Calls all function which are in the list indicated by 'channel'
        :param channel: The channel to update. Either 'on_update_point' or 'on_update_image'. If nothing, all channels
        will be updates
        """
        callables = []
        if channel == "":
            callables = [item for sublist in self.on_update.values() for item in sublist]
        elif channel in self.on_update:
            callables = self.on_update.get(channel)

        for x in callables:
            x()

    def update_points(self):
        """
        Calls all functions which are in the list 'on_update_point'.
        """
        # skip if there is no image
        if self.board.image is None:
            return
        for f in self.on_update.get("on_update_point"):
            f()

    def update_image(self):
        """
        Calls all functions which are in the list 'on_update_image'.
        """
        for f in self.on_update.get("on_update_image"):
            f()
