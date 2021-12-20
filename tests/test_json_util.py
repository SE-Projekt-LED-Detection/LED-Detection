import numpy as np


from src.BDG.model.board_model import Board, Led
from src.BDG.utils.json_util import from_json

reference = Board(name= "raspberry",author= "christoph", img_path="resources/test_image.jpg", corners=[[1, 1], [1, 10], [10, 10], [10, 1]])

reference.add_led(led=Led("led1", [10,20], radius=5, colors=["green", "blue"]))


def test_from_json():

    board = from_json("resources/model.json")
    assert (board.id == reference.id)
    assert (board.author == reference.author)
    assert (np.all(board.corners == reference.corners))



def test_to_json():
    assert False
