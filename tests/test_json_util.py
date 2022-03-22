import numpy as np

from BDG.model.board_model import Board, Led
from BDG.utils.json_util import from_json

reference = Board(name= "raspberry",author= "christoph", img_path="resources/test_image.jpg", corners=[np.array([100, 300]), np.array([200, 500])])

reference.add_led(led=Led("led1", [10,20], radius=5, colors=["green", "blue"]), relative_vector=True)


def test_from_json():

    board = from_json("resources/test_model.json")
    assert (board.id == reference.id)
    assert (board.author == reference.author)
    # assert np.all(board.corner == reference.corners)



def test_to_json():
    pass