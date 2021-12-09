"""
    Provides functions for encoding and decoding board description models from or to json
    """
import json
import io
import numpy as np
from PIL import Image
from BoardDescriptionModel import Board, Led


def from_json(json_str: str) -> Board:
    """Converts a json string to a Board object

    Args:
        json_str (str): is a valid json string describing an board object

    Raises:
        RuntimeError: if json missing required fields

    Returns:
        Board: is a Board Description model
    """
    json_dict = json.loads(json_str)
    board = Board()

    if("byte_image" in json_dict):
        board.set_image(Image.open(io.BytesIO(json_dict.get("byte_image"))))
    elif("img_path" in json_dict):
        board.set_image(Image.open(json_dict.get("img_path")))
    else:
        raise RuntimeError(msg="missing image")

    led_dicts = json_dict.get("led_objects", default=[])

    board.set_board_corners(json_dict.get("corners"))
    # True if vectors are from UL Corner -> see BoardDescripionModel
    relative_vectors = json_dict.get("relative_positions", default="True")

    for led_dict in led_dicts:
        position = np.array(led_dict.get("position"))
        led_object = Led(identifier=led_dict.get("identifier"),
                         postion=position, colors=led_dict.get("colors"))
        board.add_led(led_object, relative_vectors)

    board.author = json_dict.get("author", default="anonymous")
    board.id = json_dict.get("id")


def to_json(board: Board) -> str:
    """Converts a Board Model to a json string

    Args:
        board (Board): is a valid Board instance

    Returns:
        str: is a json representation
    """
    dict = json.dump(board)
    return dict




def to_json(led: Led) -> str:
    """Converts a led to a json string

    Args:
        led (Led): [description]

    Returns:
        str: [description]
    """
    pass