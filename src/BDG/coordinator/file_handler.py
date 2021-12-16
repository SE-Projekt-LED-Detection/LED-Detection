from src.BDG.model.board_model import Board, Led

import src.BDG.utils.json_util as jsutil
from pathlib import Path
from tkinter import filedialog as fd
class FileHandler():
    def __init__(self, parent):
        self.parent = parent

    
    def save(self):
        """saves the current board either as svg or json

        Args:
            file_name (str, optional): [description]. Defaults to "".
        """
        file_path = fd.askopenfilename()
        board = self.parent.board
        path = Path(file_path)
        assert (path.suffix in [".svg", ".json"])
        if path.suffix == ".json":
            content = jsutil.to_json(board)
        else:
            # TODO:: see svg
            content = ""
            pass
        with open(file_name, "w") as f:
            f.write(content)

        
            
    
        
            


    def load(self):
        """loads either a predifined json file as board
        or inits a new board with a selected image

        Args:
            file_path (str): [description]
        """
        file_path = fd.askopenfilename()
        file_type = Path(file_path).suffix 
        board = Board()
        if file_type == ".json":
            board = jsutil.from_json(file_path=file_path)
        elif file_type == ".svg":
            # TODO:: see svg utils
            pass
        elif file_type in [".jpg",".png", ".gif"]:
            board.set_image(file_path)
            
        self.parent.update_board(board)


