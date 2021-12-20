from src.BDG.coordinator.event_handler import EventHandler
from src.BDG.model.board_model import Board
from types import SimpleNamespace

reference = Board(name="raspberry", author="christoph", img_path="resources/test_image.jpg",
                  corners=None)
event_handler = EventHandler()
event_handler.update_board(reference)


def test_add_corner():
    event_handler.edit_handler.add_corner(SimpleNamespace(x=100, y=100))
    corner = reference.corners.pop(0)
    assert(corner[0] == corner[1] == 100)


def test_add_corner_scaling():
    event_handler.edit_handler.scaling = 0.5
    event_handler.edit_handler.add_corner(SimpleNamespace(x=100, y=100))

    assert len(reference.corners) == 1

    corner = reference.corners.pop(0)
    assert (corner[0] == corner[1] == 200)


def test_add_led_scaling():
    event_handler.edit_handler.scaling = 0.5
    event_handler.edit_handler.add_led(SimpleNamespace(x=100, y=100))

    assert len(reference.led) == 1
    led = reference.led.pop()

    assert (led.position[0] == led.position[1] == 200)

