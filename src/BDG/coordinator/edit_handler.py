
from src.BDG.model.board_model import Board
import src.BDG.utils.json_util as js_util
import numpy as np
class EditHandler():
    def __init__(self,board: Board) -> None:
        self.board = board
        self.scaling = 1.0

    def add_corner(self, event):
        corners = self.board.corners


        x = event.x * self.scaling
        y = event.y * self.scaling

        image_shape = self.board.image.shape
        if x > image_shape[0] or y > image_shape[1] or x < 0 or y < 0:
            print("invalide coordinate")
            return

        corners.append(np.array([event.x, event.y]))




    

    

