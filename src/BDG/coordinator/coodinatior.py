from model.board_model import Board
from file_handler import FileHandler
from edit_handler import EditHandler
class Coordinator():
    def __init__(self):
        self.board = Board();

        self.file_handler = FileHandler(self)
        self.edit_handler = EditHandler(self.board)

    
    def update_board(self,board: Board):
        self.board = board
    


    