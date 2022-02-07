from src.BSP.led_state import LedState


class StateTableEntry:

    def __init__(self, name, current_state: LedState, last_time_on, last_time_off):
        self.last_time_off = last_time_off
        self.last_time_on = last_time_on
        self.current_state = current_state
        self.hertz = 0
        self.name = name

