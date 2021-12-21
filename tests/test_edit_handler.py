import tkinter

from src.BDG.coordinator.event_handler import EventHandler
from src.BDG.model.CreationState import CreationState
from src.BDG.model.board_model import Board
from types import SimpleNamespace

tk = tkinter.Tk()
reference = Board(name="raspberry", author="christoph", img_path="resources/test_image.jpg",
                  corners=None)
event_handler = EventHandler()
event_handler.update_board(reference)
edit_handler = event_handler.edit_handler



def test_add_corner():
    edit_handler.add_corner(SimpleNamespace(x=100, y=100))
    corner = reference.corners.pop(0)
    assert(corner[0] == corner[1] == 100)


def test_add_corner_scaling():
    edit_handler.scaling = 0.5
    edit_handler.add_corner(SimpleNamespace(x=100, y=100))

    assert len(reference.corners) == 1

    corner = reference.corners.pop(0)
    assert (corner[0] == corner[1] == 200)


def test_add_led_scaling():
    edit_handler.scaling = 0.5
    edit_handler.add_led(SimpleNamespace(x=100, y=100))

    assert len(reference.led) == 1
    led = reference.led.pop()

    assert (led.position[0] == led.position[1] == 200)


def test_check_hovered():
    edit_handler.scaling = 1
    edit_handler.current_state.set(CreationState.LED.value)
    edit_handler.add_led(SimpleNamespace(x=80, y=80))
    assert len(edit_handler.check_hovered(80, 80)) > 0
    assert len(edit_handler.check_hovered(60, 80)) > 0
    assert len(edit_handler.check_hovered(80, 100)) > 0
    reference.led.pop()


def test_moving_point():
    edit_handler.scaling = 1
    edit_handler.current_state.set(CreationState.LED.value)
    start_position = SimpleNamespace(x=80, y=80)
    edit_handler.add_led(start_position)

    # Simulate click on LED
    edit_handler.add_led(start_position)

    # Try to move outside image
    edit_handler.moving_point(SimpleNamespace(x=reference.image.shape[1] + 1, y=reference.image.shape[0] + 1))
    assert reference.led[0].position[0] == reference.led[0].position[1] == 80

    # Try to move to negative coordinates
    edit_handler.moving_point(SimpleNamespace(x=-1, y=-1))
    assert reference.led[0].position[0] == reference.led[0].position[1] == 80

    # Move a bit
    edit_handler.moving_point(SimpleNamespace(x=10, y=10))
    assert reference.led[0].position[0] == reference.led[0].position[1] == 10

    edit_handler.current_state.set(CreationState.BOARD.value)
    edit_handler.add_corner(start_position)

    # Simulate click on corner
    edit_handler.add_corner(start_position)
    # Move a bit
    edit_handler.moving_point(SimpleNamespace(x=10, y=10))
    assert reference.corners[0][0] == reference.corners[0][1] == 10

    # Cleanup
    reference.corners.pop()
    reference.led.clear()
    edit_handler.active_circle = None



