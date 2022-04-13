import tkinter
from unittest.mock import MagicMock, Mock

import pytest

from BDG.coordinator.event_handler import EventHandler
from BDG.model.board_model import Board

tk = tkinter.Tk()
global event_handler
global reference

@pytest.fixture(autouse=True)
def setup():
    global reference
    global event_handler
    reference = Board(name="raspberry", author="christoph", img_path="resources/test_model.jpg",
                      corners=None)
    event_handler = EventHandler()
    event_handler.update_board(reference)


def test_set_board():
    event_handler.update_board(reference)
    assert event_handler.board.id == reference.id

def test_send_update():

    points_updated = Mock()
    images_updated = Mock()

    event_handler.on_update.get("on_update_point").append(points_updated)
    event_handler.on_update.get("on_update_image").append(images_updated)

    event_handler.update("on_update_point")
    event_handler.update("on_update_image")

    points_updated.assert_called_once()
    images_updated.assert_called_once()

