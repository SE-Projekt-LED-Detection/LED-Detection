import os

import cv2

from src.BDG.model.board_model import Board, Led

import src.BDG.utils.json_util as jsutil
from pathlib import Path
from tkinter import filedialog as fd
from zipfile import ZipFile
class FileHandler():
    def __init__(self, parent):
        self.parent = parent

    
    def save(self):
        """saves the current board either as svg or json

        Args:
            file_name (str, optional): [description]. Defaults to "".
        """
        f = fd.asksaveasfile(mode='w', defaultextension=".json")
        path = Path(f.name)
        file_name = Path(path.name)
        current_dir = os.getcwd()
        # change the working directory for using relative paths
        os.chdir(path.parent.__str__())

        path = Path(path.name)

        zip_name = path.with_suffix(".zip").__str__()
        image_path = path.with_suffix(".jpg").__str__()

        board = self.parent.board
        board_dict = board.__dict__
        cv2.imwrite(image_path, board_dict['image'])
        board_dict['image_path'] = image_path
        del board_dict['image']
        assert (path.suffix in [".svg", ".json"])
        if path.suffix == ".json":
            content = jsutil.to_json(board_dict)
            f.write(content)

        else:
            print("not implemented yet!")
            # TODO:: see svg
            content = ""
        f.close()
        with ZipFile(zip_name, 'w') as myzip:
            myzip.write(path.__str__())
            myzip.write(image_path)
        os.chdir(current_dir)





    def load(self):
        """loads either a predifined json file as board
        or inits a new board with a selected image

        Args:
            file_path (str): [description]
        """
        file_path = Path(fd.askopenfilename())
        current_dir = os.getcwd()

        os.chdir(file_path.parent.__str__())
        file_path = Path(file_path.name)
        file_type = file_path.suffix

        board = Board()
        if file_type == ".json":
            board = jsutil.from_json(file_path=file_path.__str__())
        elif file_type == ".svg":
            # TODO:: see svg utils
            pass
        elif file_type in [".jpg",".png", ".gif"]:
            board.set_image(file_path)


        self.parent.update_board(board)
        os.chdir(current_dir)




