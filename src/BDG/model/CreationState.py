from enum import Enum


class CreationState(Enum):
    """
    The current placement mode. If it is BOARD, an anchor point is placed on left mouse click,
    if it is LED a LED is placed.
    """
    BOARD = 0
    LED = 1