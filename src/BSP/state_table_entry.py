from BSP.led_state import LedState


class StateTableEntry:
    """
    Represents an entry of the state table.
    Contains the name, current state, last time on and last time off of an LED.
    Last time of and off are timestamp based.
    """

    def __init__(self, name, current_state: LedState, last_time_on, last_time_off):
        self.last_time_off = last_time_off
        self.last_time_on = last_time_on
        self.current_state = current_state
        self.hertz = 0
        self.name = name

