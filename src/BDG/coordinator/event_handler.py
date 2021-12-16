from src.BDG.model.board_model import Board
from src.BDG.coordinator.file_handler import FileHandler
from src.BDG.coordinator.edit_handler import EditHandler

class EventHandler():
    def __init__(self):
        self.board = Board();
        self.on_update = {
            "on_update_point": [],
            "on_update_image": []

        }

        self.file_handler = FileHandler(self)
        self.edit_handler = EditHandler(self)

    
    def update_board(self,board: Board):
        self.board = board
        print(board)


    def update_points(self):
        for f in self.on_update.get("on_update_point"):
            f()

    def update_image(self):
        for f in self.on_update.get("on_update_image"):
            f()
    
