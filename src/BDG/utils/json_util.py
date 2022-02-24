"""
    Provides functions for encoding and decoding board description models from or to json
    """
import json
import os

import numpy as np
from src.BDG.model.board_model import Board, Led
import cv2
from numpyencoder import NumpyEncoder

from src.BDG.utils.util_functions import decode_img_data


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

    elif ("image_path" in json_dict):
        image = cv2.imread(os.path.join(os.path.dirname(file.name), json_dict.get("image_path")))
    else:
        raise RuntimeError()
    board.set_image(image)
    led_dicts = json_dict.get("led")

    board.set_board_corners(json_dict.get("corners"))
    # True if vectors are from UL Corner -> see BoardDescripionModel
    relative_vectors = json_dict.get("relative_positions", True)

    for led_dict in led_dicts:
        position = np.array(led_dict.get("position"))
        led_object = Led(identifier=led_dict.get("id"), radius=led_dict.get("radius"),
                         position=position, colors=led_dict.get("colors"))
        board.add_led(led_object, relative_vectors)

    board.author = json_dict.get("author", "anonymous")
    board.id = json_dict.get("id")
    return board


def to_json(board_dict: dict) -> str:
    """Converts a Board Model to a json string

    Args:
        board (Board): is a valid Board instance

    Returns:
        str: is a json representation
    """


    # make nd_array serializable

    board_dict["led"] = list(map(__led_to_dict,board_dict["led"]))

    return json.dumps(board_dict, cls=NumpyEncoder)

def __led_to_dict(led: Led) -> dict:
    """convertst a led model to a json string


    :param led: is an led object
    :return: a serializable dictionary of the object led
    """

    led_dict = led.__dict__
    led_dict["position"] =led_dict["position"].tolist()
    return led_dict

