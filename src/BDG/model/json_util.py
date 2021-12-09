"""
    Provides functions for encoding and decoding board description models from or to json
    """
import json
import numpy as np
from src.BDG.model.board_model import Board, Led
from src.BDG.model.util_functions import decode_img_data
import cv2
import matplotlib.pyplot as plt


def from_json(file_path: str):
    with open(file_path, "r") as file:
        return __from_json(file)


def __from_json(file) -> Board:
    """Converts a json string to a Board object

    Args:
        json_str (str): is a valid json string describing an board object

    Raises:
        RuntimeError: if json missing required fields

    Returns:
        Board: is a Board Description model
    """
    json_dict = json.load(file)
    board = Board()

    if ("byte_image" in json_dict):
        image = decode_img_data(json_dict.get("byte_image"))
        board.set_image(pil_image=image)
    elif ("img_path" in json_dict):
        board.set_image(cv2.imread(json_dict.get("image_path")))
    else:
        raise RuntimeError()

    led_dicts = json_dict.get("led")

    board.set_board_corners(json_dict.get("corners"))
    # True if vectors are from UL Corner -> see BoardDescripionModel
    relative_vectors = json_dict.get("relative_positions",True)

    for led_dict in led_dicts:
        position = np.array(led_dict.get("position"))
        led_object = Led(identifier=led_dict.get("id"),radius=led_dict.get("radius"),
                         position=position, colors=led_dict.get("colors"))
        board.add_led(led_object, relative_vectors)

    board.author = json_dict.get("author", "anonymous")
    board.id = json_dict.get("id")
    return board


def to_json(board: Board) -> str:
    """Converts a Board Model to a json string

    Args:
        board (Board): is a valid Board instance

    Returns:
        str: is a json representation
    """
    board_dict = json.dumps(board.__dict__)
    return board_dict
