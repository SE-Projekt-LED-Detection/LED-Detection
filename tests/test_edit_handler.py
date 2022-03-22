import tkinter

import pytest

from BDG.coordinator.event_handler import EventHandler
from BDG.model.CreationState import CreationState
from BDG.model.board_model import Board
from types import SimpleNamespace

tk = tkinter.Tk()
reference = Board(name="raspberry", author="christoph", img_path="resources/test_model.jpg",
                  corners=None)
event_handler = EventHandler()
event_handler.update_board(reference)
edit_handler = event_handler.edit_handler
start_position = SimpleNamespace(x=80, y=80)

assert reference.image is not None, "Image has not been loaded"


@pytest.fixture(autouse=True)
def setup():
    global reference
    global event_handler
    global edit_handler
    reference = Board(name="raspberry", author="christoph", img_path="resources/test_model.jpg",
                      corners=None)
    event_handler = EventHandler()
    event_handler.update_board(reference)
    edit_handler = event_handler.edit_handler


def test_add_delete_undo_redo_corner():
    """
    Tests adding, deleting, undo/redo adding a corner
    """
    edit_handler.add_corner(SimpleNamespace(x=100, y=100))
    corner = reference.corners[0]
    assert(corner[0] == corner[1] == 100)

    edit_handler.delete_point(SimpleNamespace(x=100, y=100))

    assert len(reference.corners) == 0

    # Add corner again
    edit_handler.add_corner(SimpleNamespace(x=100, y=100))

    edit_handler.undo()

    # Corner undone
    assert len(reference.corners) == 0

    edit_handler.redo()

    # Corner redone
    corner = reference.corners[0]
    assert (corner[0] == corner[1] == 100)

    edit_handler.delete_point(SimpleNamespace(x=100, y=100))


def test_add_delete_undo_redo_led():
    """
    Tests adding, deleting, undo/redo adding a led
    """
    edit_handler.current_state.set(CreationState.LED.value)
    edit_handler.add_led(SimpleNamespace(x=100, y=100))


    assert len(reference.led) == 1

    led_id = "identifier1"
    reference.led[0].id = led_id

    # Undo
    edit_handler.undo()
    assert len(reference.led) == 0

    # Redo
    edit_handler.redo()
    assert len(reference.led) == 1
    assert reference.led[0].id == led_id  # ID still the same?


    # Delete
    edit_handler.delete_point(SimpleNamespace(x=100, y=100))
    assert len(reference.led) == 0

    # Cleanup
    edit_handler.current_state.set(CreationState.BOARD.value)


def test_add_corner_scaling():
    """
    Tests whether when scaling is set the coordinates of a corner are scaled in accordance
    """
    edit_handler.scaling = 0.5
    edit_handler.add_corner(SimpleNamespace(x=100, y=100))

    assert len(reference.corners) == 1

    corner = reference.corners.pop(0)
    assert (corner[0] == corner[1] == 200)


def test_add_led_scaling():
    """
    Tests whether when scaling is set the coordinates of a led are scaled in accordance
    """
    edit_handler.scaling = 0.5
    edit_handler.add_led(SimpleNamespace(x=100, y=100))

    assert len(reference.led) == 1
    led = reference.led.pop()

    assert (led.position[0] == led.position[1] == 200)

    edit_handler.scaling = 1


def test_check_hovered():
    """
    Tests if hovering over a led returns the led
    """
    edit_handler.scaling = 1
    edit_handler.current_state.set(CreationState.LED.value)
    edit_handler.add_led(SimpleNamespace(x=80, y=80))
    assert len(edit_handler.check_hovered(80, 80)) > 0
    assert len(edit_handler.check_hovered(60, 80)) > 0
    assert len(edit_handler.check_hovered(80, 100)) > 0
    reference.led.pop()


def test_moving_point():
    """
    Tests moving a LED, try to move outside, to negative coordinates and tests to move corner
    """
    edit_handler.scaling = 1
    edit_handler.current_state.set(CreationState.LED.value)
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


def test_on_mousewheel():
    """
    Tests resizing LED with the mousewheel
    """
    edit_handler.scaling = 1
    edit_handler.current_state.set(CreationState.LED.value)
    edit_handler.add_led(start_position)

    org_radius = reference.led[0].radius

    scrolling_up_event = SimpleNamespace(x=80, y=80, num=4, delta=120)
    scrolling_down_event = SimpleNamespace(x=80, y=80, num=5, delta=-120)

    edit_handler.on_mousewheel(scrolling_up_event)

    assert reference.led[0].radius == org_radius + 1

    edit_handler.on_mousewheel(scrolling_down_event)

    assert reference.led[0].radius == org_radius


